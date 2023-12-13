"""Mixins for vpn_app views."""
from abc import ABC

from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy


class ChangeSuccessURLMixin:
    """Rewrite get_success_url method."""

    def get_success_url(self):
        """Get success url for redirect."""
        if self.request.user.is_anonymous:
            return super().get_success_url()
        return reverse_lazy("vpn:account", kwargs={"pk": self.request.user.id})


class CustomUserPassesTestMixin(UserPassesTestMixin, ABC):
    """Customize UserPassesTestMixin, add test_func method."""

    def test_func(self) -> bool:
        """Test whether user is user."""
        if self.request.user.is_anonymous:
            return False
        pk = self.request.user.pk
        return pk == self.kwargs.get("owner_id") or pk == self.kwargs.get("pk")
