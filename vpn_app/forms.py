"""Forms for vpn_app."""
import typing

from django import forms
from django.contrib.auth.models import User

from vpn_app.models import VpnSite


class UserAccountForm(forms.ModelForm):
    """Form for User model."""

    class Meta:  # noqa WPS306
        """Class Meta for UserAccountForm."""

        model = User
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Rewrite fields class."""
        super().__init__(*args, **kwargs)
        fields = self.fields
        fields["username"].widget.attrs["class"] = "custom-input custom-input-height"
        fields["email"].widget.attrs["class"] = "custom-input custom-input-height"
        fields["first_name"].widget.attrs["class"] = "custom-input custom-input-height"
        fields["last_name"].widget.attrs["class"] = "custom-input custom-input-height"


class VpnSiteCreateForm(forms.ModelForm):
    """Form for PersonalSite model instance creation."""

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Rewrite fields styling."""
        super().__init__(*args, **kwargs)
        fields = self.fields
        fields["name"].widget.attrs["class"] = "custom-input custom-input-height"
        fields["domain"].widget.attrs["class"] = "custom-input custom-input-height"
        fields["scheme"].widget.attrs["class"] = "custom-input custom-input-height"

    class Meta:  # noqa WPS306
        """Class Meta for PersonalSiteCreateForm."""

        model = VpnSite
        fields = ("name", "domain", "scheme")
