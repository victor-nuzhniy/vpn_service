"""Views for vpn_app."""
import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import generic

from project_services import mixins
from vpn_app import forms
from vpn_app.app_views import BaseVpnProxyView
from vpn_app.models import VpnSite


class IndexView(generic.TemplateView):
    """Index view."""

    template_name = "vpn_app/index.html"
    extra_context = {"title": "Welcome"}


class CreateSiteLinkView(
    LoginRequiredMixin,
    mixins.ChangeSuccessURLMixin,
    generic.FormView,
):
    """Create site view."""

    form_class = forms.VpnSiteCreateForm
    template_name = "vpn_app/site/create_site_link.html"
    extra_context = {"title": "Create vpn link"}
    success_url = reverse_lazy("auth:sign_up")

    def form_valid(self, form: forms.VpnSiteCreateForm) -> HttpResponse:
        """Create personal site."""
        form_data: dict = form.cleaned_data
        if self.request.user.is_authenticated:
            VpnSite(**form_data, owner=self.request.user).save()
        return super().form_valid(form)


class UpdateSiteLinkView(
    mixins.CustomUserPassesTestMixin,
    mixins.ChangeSuccessURLMixin,
    generic.UpdateView,
):
    """Update site view."""

    form_class = forms.VpnSiteCreateForm
    template_name = "vpn_app/site/update_site_link.html"
    extra_context = {"title": "Update site link"}
    success_url = reverse_lazy("auth:sign_up")
    slug_field = "domain"

    def get_queryset(self) -> QuerySet:
        """Return queryset using current user."""
        if self.request.user.is_authenticated:
            return VpnSite.objects.filter(owner=self.request.user)
        return VpnSite.objects.filter(owner=None)


class DeleteSiteLinkView(  # type: ignore
    mixins.CustomUserPassesTestMixin,
    mixins.ChangeSuccessURLMixin,
    generic.DeleteView,
):
    """Delete PersonalSite model instance."""

    model = VpnSite
    template_name = "vpn_app/site/delete_site_link.html"
    extra_context = {"title": "Delete site link"}
    success_url = reverse_lazy("auth:sign_up")
    slug_field = "domain"

    def get_queryset(self) -> QuerySet:
        """Return queryset using current user."""
        if self.request.user.is_authenticated:
            return VpnSite.objects.filter(owner=self.request.user)
        return VpnSite.objects.filter(owner=None)


class AccountView(
    mixins.CustomUserPassesTestMixin,
    mixins.ChangeSuccessURLMixin,
    generic.UpdateView,
):
    """Update user information."""

    model = User
    form_class = forms.UserAccountForm
    template_name = "vpn_app/account.html"
    extra_context = {"title": "Personal info"}
    success_url = reverse_lazy("auth:sign_up")

    def get_context_data(self, **kwargs: typing.Any) -> dict:
        """Get context data."""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            context["vpn_sites"] = VpnSite.objects.filter(owner=user)
        return context


class VpnProxyView(BaseVpnProxyView):
    """Proxy view."""

    retries = 2
    add_x_forwarded = True
