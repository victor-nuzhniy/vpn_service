"""Views for vpn_app."""
from typing import Dict, Optional

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DeleteView, FormView, TemplateView, UpdateView
from revproxy.utils import should_stream
from revproxy.views import ProxyView

from vpn_app.forms import (
    CustomAuthForm,
    CustomPasswordChangeForm,
    CustomUserCreationForm,
    UserAccountForm,
    VpnSiteCreateForm,
)
from vpn_app.mixins import ChangeSuccessURLMixin, CustomUserPassesTestMixin
from vpn_app.models import VpnSite
from vpn_app.tasks import add_links_number, add_loaded_volume, add_sended_volume
from vpn_app.utils import modify_response


class IndexView(TemplateView):
    """Index view."""

    template_name = "vpn_app/index.html"
    extra_context = {"title": "Welcome"}


class RegisterView(ChangeSuccessURLMixin, FormView):
    """View for user registration."""

    form_class = CustomUserCreationForm
    template_name = "vpn_app/auth/user_creation_form.html"
    extra_context = {"title": "Sign up"}
    success_url = reverse_lazy("vpn:sign_up")

    def form_valid(self, form: CustomUserCreationForm) -> HttpResponseRedirect:
        """Create new user and login."""
        user: User = form.save()
        login(self.request, user)
        return super().form_valid(form)


class CustomLoginView(ChangeSuccessURLMixin, LoginView):
    """Login view."""

    extra_context = {"title": "Sign in"}
    next_page = "vpn:sign_up"
    redirect_authenticated_user = True
    template_name = "vpn_app/auth/login.html"
    form_class = CustomAuthForm


class CustomPasswordChangeView(ChangeSuccessURLMixin, PasswordChangeView):
    """Class view for user password changing."""

    success_url = reverse_lazy("vpn:signup")
    template_name = "vpn_app/auth/password_change.html"
    extra_context = {"title": "Password change"}
    form_class = CustomPasswordChangeForm


class CreateSiteLinkView(LoginRequiredMixin, ChangeSuccessURLMixin, FormView):
    """Create site view."""

    form_class = VpnSiteCreateForm
    template_name = "vpn_app/site/create_site_link.html"
    extra_context = {"title": "Create vpn link"}
    success_url = reverse_lazy("vpn:sign_up")

    def form_valid(self, form) -> HttpResponseRedirect:
        """Create personal site."""
        data: Dict = form.cleaned_data
        VpnSite(**data, owner=self.request.user).save()
        return super().form_valid(form)


class UpdateSiteLinkView(CustomUserPassesTestMixin, ChangeSuccessURLMixin, UpdateView):
    """Update site view."""

    form_class = VpnSiteCreateForm
    template_name = "vpn_app/site/update_site_link.html"
    extra_context = {"title": "Update site link"}
    success_url = reverse_lazy("vpn:sign_up")
    slug_field = "domain"

    def get_queryset(self):
        """Return queryset using current user."""
        return VpnSite.objects.filter(owner=self.request.user)


class DeleteSiteLinkView(CustomUserPassesTestMixin, ChangeSuccessURLMixin, DeleteView):
    """Delete PersonalSite model instance."""

    model = VpnSite
    template_name = "vpn_app/site/delete_site_link.html"
    extra_context = {"title": "Delete site link"}
    success_url = reverse_lazy("vpn:sign_up")
    slug_field = "domain"

    def get_queryset(self):
        """Return queryset using current user."""
        return VpnSite.objects.filter(owner=self.request.user)


class AccountView(CustomUserPassesTestMixin, ChangeSuccessURLMixin, UpdateView):
    """Update user information."""

    model = User
    form_class = UserAccountForm
    template_name = "vpn_app/account.html"
    extra_context = {"title": "Personal info"}
    success_url = reverse_lazy("vpn:sign_up")

    def get_context_data(self, **kwargs) -> Dict:
        """Get context data."""
        context = super().get_context_data(**kwargs)
        user: User = self.request.user
        context["vpn_sites"] = VpnSite.objects.filter(owner=user)
        return context


@method_decorator(csrf_exempt, name="dispatch")
class VpnProxyView(ProxyView):
    """Proxy view."""

    retries = 2
    add_x_forwarded = True

    def __init__(self, *args, **kwargs):
        """Rewrite __init__ method, add 'domain' attr."""
        self.domain: Optional[str] = None
        super().__init__(*args, **kwargs)

    def get_quoted_path(self, path) -> str:
        """Rewrite get_quoted_path method, hook for perform_additional_operations."""
        path = super().get_quoted_path(path)
        return self.perform_additional_operations(path)

    def perform_additional_operations(self, path) -> str:
        """
        Check whether user is login and path content.

        If path starts with 'localhost', get domain, otherwise get it from cookies.
        If not domain or user is anonimous - raise 404.
        Try to get VpnSite instance and if it is, set upstream property, otherwise
        raise 404.
        In case of 'localhost' present in path, clean it.
        Return path (modified or not).
        """
        user = self.request.user
        if self.request.path.startswith("/localhost") or self.request.path.startswith(
            "localhost"
        ):
            path_list = self.request.path.split("localhost")
            path = path_list[-1]
            path_list = path.split("/")
            self.domain = path_list[1]
            path = "/".join(path_list[2:])
        else:
            self.domain = self.request.COOKIES.get("user_domain")
        if not self.domain or user.is_anonymous:
            raise Http404
        if not (
            vpn_site := VpnSite.objects.filter(
                owner=user, domain__startswith=self.domain
            ).first()
        ):
            raise Http404

        self.upstream = f"{vpn_site.scheme}://{self.domain}"
        if (
            self.request.headers.get("Sec-Fetch-Dest") == "document"
            and self.request.headers.get("Sec-Fetch-Mode") == "navigate"
        ):
            add_links_number.delay(user.id, self.domain)
        if volume := self.request.headers.get("Content-Length", 0):
            add_loaded_volume.delay(user.id, self.domain, volume)
        return path

    def _created_proxy_response(self, request, path):
        """Add functionality to method."""
        response = super()._created_proxy_response(request, path)
        self._set_content_type(request, response)
        content_length = response.headers.get("Content-Length", 0)
        if content_length:
            add_sended_volume.delay(request.user.id, self.domain, content_length)
        if not should_stream(response):
            modify_response(response, request.get_host(), self.domain)
        return response

    def _replace_host_on_redirect_location(self, request, proxy_response):
        """Rewrite method to modify links with given domain name."""
        super()._replace_host_on_redirect_location(request, proxy_response)
        location = proxy_response.headers.get("Location")
        if location:
            if location:
                if request.is_secure():
                    scheme = "https://"
                else:
                    scheme = "http://"
                request_host = scheme + request.get_host() + "/localhost/" + self.domain
                if location.startswith("http"):
                    upstream_host_http = "http://" + self._parsed_url.netloc
                    upstream_host_https = "https://" + self._parsed_url.netloc
                    location = location.replace(upstream_host_http, request_host)
                    location = location.replace(upstream_host_https, request_host)
                else:
                    location = request_host + location
                proxy_response.headers["Location"] = location
                self.log.debug(
                    "Proxy response LOCATION: %s", proxy_response.headers["Location"]
                )

    def dispatch(self, request, path):
        """Rewrite dispatch method. Add 'user_domain' cookie."""
        response = super().dispatch(request, path)
        response.set_cookie(key="user_domain", value=self.domain)
        return response
