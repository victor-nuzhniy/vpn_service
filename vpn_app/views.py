"""Views for vpn_app."""
from typing import Dict

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView, FormView, TemplateView, UpdateView

from vpn_app.forms import (
    CustomAuthForm,
    CustomPasswordChangeForm,
    CustomUserCreationForm,
    UserAccountForm,
    VpnSiteCreateForm,
)
from vpn_app.mixins import ChangeSuccessURLMixin, CustomUserPassesTestMixin
from vpn_app.models import VpnSite


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
    slug_field = "url"

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


class VpnView(View):
    """Vpn view."""

    def get(self, request, *args, **kwargs):
        """Handle get request."""
        return HttpResponse("Hello World!")
