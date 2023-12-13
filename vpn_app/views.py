"""Views for vpn_app."""
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView

from vpn_app.forms import (
    CustomAuthForm,
    CustomPasswordChangeForm,
    CustomUserCreationForm,
)
from vpn_app.mixins import ChangeSuccessURLMixin


class IndexView(TemplateView):
    """Index view."""

    template_name = "vpn_app/index.html"
    extra_context = {"title": "Welcome"}


class RegisterView(ChangeSuccessURLMixin, FormView):
    """View for user registration."""

    form_class = CustomUserCreationForm
    template_name = "vpn/auth/user_creation_form.html"
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


class VpnView(View):
    """Vpn view."""

    def get(self, request, *args, **kwargs):
        """Handle get request."""
        return HttpResponse("Hello World!")
