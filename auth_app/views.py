"""Class and function views for auth_app."""
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView

from auth_app.forms import (
    CustomAuthForm,
    CustomPasswordChangeForm,
    CustomUserCreationForm,
)
from project_services.mixins import ChangeSuccessURLMixin


class RegisterView(ChangeSuccessURLMixin, FormView):
    """View for user registration."""

    form_class = CustomUserCreationForm
    template_name = "auth_app/user_creation_form.html"
    extra_context = {"title": "Sign up"}
    success_url = reverse_lazy("auth:sign_up")

    def form_valid(self, form: CustomUserCreationForm) -> HttpResponse:
        """Create new user and login."""
        user: User = form.save()
        login(self.request, user)
        return super().form_valid(form)


class CustomLoginView(ChangeSuccessURLMixin, LoginView):
    """Login view."""

    extra_context = {"title": "Sign in"}
    next_page = "auth:sign_up"
    redirect_authenticated_user = True
    template_name = "auth_app/login.html"
    form_class = CustomAuthForm


class CustomPasswordChangeView(ChangeSuccessURLMixin, PasswordChangeView):
    """Class view for user password changing."""

    success_url = reverse_lazy("auth:signup")
    template_name = "auth_app/password_change.html"
    extra_context = {"title": "Password change"}
    form_class = CustomPasswordChangeForm
