"""Module for configuration for auth_app."""
from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    """Class for configuration for auth_app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "auth_app"
