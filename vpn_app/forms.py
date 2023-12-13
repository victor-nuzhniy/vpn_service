"""Forms for vpn_app."""
from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)
from django.contrib.auth.models import User

from vpn_app.models import VpnSite


class CustomUserCreationForm(UserCreationForm):
    """Customize UserCreationForm fields."""

    def __init__(self, *args, **kwargs) -> None:
        """Restyle fields classes."""
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs[
            "class"
        ] = "custom-input custom-input-height"
        self.fields["password1"].widget.attrs[
            "class"
        ] = "custom-input custom-input-height"
        self.fields["password2"].widget.attrs[
            "class"
        ] = "custom-input custom-input-height"


class CustomAuthForm(AuthenticationForm):
    """Customize AuthenticationForm fields classes."""

    def __init__(self, *args, **kwargs) -> None:
        """Restyle fields classes."""
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs[
            "class"
        ] = "custom-input custom-input-height"
        self.fields["password"].widget.attrs[
            "class"
        ] = "custom-input custom-input-height"


class CustomPasswordChangeForm(PasswordChangeForm):
    """Customize PasswordChangeForm fields."""

    def __init__(self, *args, **kwargs) -> None:
        """Restyle fields classes."""
        super().__init__(*args, **kwargs)
        self.fields["old_password"].widget.attrs[
            "class"
        ] = "custom-input custom-input-height"
        self.fields["new_password1"].widget.attrs[
            "class"
        ] = "custom-input custom-input-height"
        self.fields["new_password2"].widget.attrs[
            "class"
        ] = "custom-input custom-input-height"


class UserAccountForm(forms.ModelForm):
    """Form for User model."""

    class Meta:
        """Class Meta for UserAccountForm."""

        model = User
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args, **kwargs) -> None:
        """Rewrite fields class."""
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs[
            "class"
        ] = "custom-input custom-input-height"
        self.fields["email"].widget.attrs["class"] = "custom-input custom-input-height"
        self.fields["first_name"].widget.attrs[
            "class"
        ] = "custom-input custom-input-height"
        self.fields["last_name"].widget.attrs[
            "class"
        ] = "custom-input custom-input-height"


class VpnSiteCreateForm(forms.ModelForm):
    """Form for PersonalSite model instance creation."""

    def __init__(self, *args, **kwargs):
        """Rewrite fields styling."""
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs["class"] = "custom-input custom-input-height"
        self.fields["domain"].widget.attrs["class"] = "custom-input custom-input-height"

    class Meta:
        """Class Meta for PersonalSiteCreateForm."""

        model = VpnSite
        fields = ("name", "domain")
