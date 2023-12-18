"""Views for vpn_app."""
from typing import Dict, Optional

import bs4
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse_lazy
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
from vpn_app.utils import find_sample_without_word


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


class VpnProxyView(ProxyView):
    """Proxy view."""

    def __init__(self, *args, **kwargs):
        """Rewrite __init__ method, add 'domain' attr."""
        self.domain: Optional[str] = None
        super().__init__(*args, **kwargs)

    def get_quoted_path(self, path) -> str:
        """Rewrite get_quoted_path method, hook for perform_additional_operations."""
        path = self.perform_additional_operations(path)
        return super().get_quoted_path(path)

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
        if self.request.path.startswith("/localhost"):
            path_list = path.split("/")
            self.domain = path_list[0]
            path = "/".join(path_list[1:])
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

        if self.request.path.startswith("/localhost"):
            add_links_number.delay(user.id, self.domain)
        if volume := self.request.headers.get("Content-Length", 0):
            add_loaded_volume.delay(user.id, self.domain, volume)

        return path

    def _created_proxy_response(self, request, path):
        """Add functionality to method."""
        response = super()._created_proxy_response(request, path)
        self._set_content_type(request, response)
        content_length = response.headers.get("content-length", 0)
        content_length_uppper = response.headers.get("Content-Length", 0)
        if content_length or content_length_uppper:
            add_sended_volume.delay(
                request.user.id, self.domain, content_length, content_length_uppper
            )
        if not should_stream(response):
            xsoup = bs4.BeautifulSoup(response.data or b"", "html.parser")
            for elem in xsoup.find_all(
                "a", href=lambda x: find_sample_without_word(x, "http")
            ):
                elem["href"] = f"localhost/{self.domain}/{elem['href']}"
            response._body = xsoup.prettify()
        return response

    def dispatch(self, request, path):
        """Rewrite dispatch method. Add 'user_domain' cookie."""
        response = super().dispatch(request, path)
        response.set_cookie(key="user_domain", value=self.domain)
        return response
