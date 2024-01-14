"""Mixins for vpn_app views."""
import typing
from abc import ABC

from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpRequest
from django.urls import reverse_lazy
from django.views.generic import FormView

if typing.TYPE_CHECKING:
    _Base = FormView
else:
    _Base = object


class ChangeSuccessURLMixin(_Base):
    """Rewrite get_success_url method."""

    def get_success_url(self) -> str:
        """Get success url for redirect."""
        if self.request.user.is_anonymous:
            return super().get_success_url()
        return reverse_lazy("vpn:account", kwargs={"pk": self.request.user.id})


class RequestAttribute(typing.Protocol):
    """Class with request and kwargs properties."""

    @property
    def request(self) -> HttpRequest:
        """Request attr."""

    @property
    def kwargs(self) -> dict:
        """Kwargs attr."""


class CustomUserPassesTestMixin(UserPassesTestMixin, ABC):
    """Customize UserPassesTestMixin, add test_func method."""

    def test_func(self: RequestAttribute) -> bool:
        """Test whether user is user."""
        if self.request.user.is_anonymous:
            return False
        pk = self.request.user.pk
        return pk in {self.kwargs.get("owner_id"), self.kwargs.get("pk")}
