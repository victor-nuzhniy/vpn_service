"""Views for vpn_app."""
from typing import Dict, Optional
from urllib.parse import urlsplit, urlunsplit

import bs4
import requests
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.db.models import F
from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseRedirect,
    StreamingHttpResponse,
)
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView, FormView, TemplateView, UpdateView
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
from vpn_app.utils import find_sample, find_sample_without_word


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


class VpnView(LoginRequiredMixin, View):
    """Vpn view."""

    def get(self, request, *args, **kwargs):
        """Handle get request."""
        path: str = self.kwargs.get("path")
        domain: Optional[str] = None
        if path_list := path.split("/"):
            domain = path_list[0]
        user = request.user
        if domain and not (
            vpn_site := VpnSite.objects.filter(
                owner=user, domain__startswith=domain
            ).first()
        ):
            return HttpResponseNotFound(
                f"<h2>Error. You haven't registered site with domain {domain}.</h2>"
            )
        if (
            sec_fetch_dest := request.headers.get("Sec-Fetch_Dest")
        ) and sec_fetch_dest in {
            "image",
            "video",
            "worker",
            "sharedworker",
            "serviceworker",
            "paintworklet",
            "audio",
            "audioworklet",
        }:
            url = f"http://{request.path[11:]}"
            response = requests.request(
                method="GET",
                url=url,
                headers=request.headers,
                timeout=5.0,
                stream=True,
            )

            return StreamingHttpResponse(
                response.raw,
                # content_type=response.headers.get('content-type'),
                headers=response.headers,
                status=response.status_code,
                reason=response.reason,
            )

        response = requests.request(
            method=request.method,
            url=f"http://{request.path[11:]}",
            headers=request.headers,
            cookies=request.COOKIES,
            files=request.FILES,
            timeout=20.0,
        )

        vpn_site.sended_volume = F("sended_volume") + int(
            response.headers.get("Content-Length", "0")
        )
        content_type = response.headers.get("Content-Type")
        if content_type and content_type.split(";")[0] in {
            "text/plain",
            "text/html",
            "text/csv",
            "text/xml",
        }:
            vpn_site.used_links_number = F("used_links_number") + 1
        vpn_site.save()
        host = request.META["HTTP_HOST"]
        xsoup = bs4.BeautifulSoup(response.text, "html.parser")
        for elem in xsoup.find_all("a", href=lambda x: find_sample(x, domain)):
            parsed_url = urlsplit(elem["href"])
            elem["href"] = urlunsplit(
                (
                    parsed_url.scheme,
                    f"{host}/localhost/{parsed_url.netloc}",
                    parsed_url.path,
                    parsed_url.query,
                    parsed_url.fragment,
                )
            )
        for elem in xsoup.find_all(href=lambda x: find_sample_without_word(x, "http")):
            elem["href"] = urlunsplit(
                (
                    "http",  # TODO check solution concerning scheme
                    f"{host}/localhost/{domain}",
                    elem["href"],
                    "",
                    "",
                )
            )
        for elem in xsoup.find_all(src=lambda x: find_sample_without_word(x, "http")):
            elem["src"] = urlunsplit(
                (
                    "http",  # TODO check solution concerning scheme
                    f"{host}/localhost/{domain}",
                    elem["src"],
                    "",
                    "",
                )
            )

        final_response = HttpResponse(
            content=xsoup.prettify(),
            status=response.status_code,
            headers=response.headers,
        )
        del final_response.headers["Connection"]
        del final_response.headers["Keep-Alive"]
        return final_response


class VpnProxyView(ProxyView):
    """Proxy view."""

    _upstream = "https://www.google.com.ua"
