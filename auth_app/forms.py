"""Forms for aut_app."""
import typing

from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)


class CustomUserCreationForm(UserCreationForm):
    """Customize UserCreationForm fields."""

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Restyle fields classes."""
        fields = self.fields
        super().__init__(*args, **kwargs)
        fields["username"].widget.attrs["class"] = "custom-input custom-input-height"
        fields["password1"].widget.attrs["class"] = "custom-input custom-input-height"
        fields["password2"].widget.attrs["class"] = "custom-input custom-input-height"


class CustomAuthForm(AuthenticationForm):
    """Customize AuthenticationForm fields classes."""

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Restyle fields classes."""
        super().__init__(*args, **kwargs)
        fields = self.fields
        fields["username"].widget.attrs["class"] = "custom-input custom-input-height"
        fields["password"].widget.attrs["class"] = "custom-input custom-input-height"


class CustomPasswordChangeForm(PasswordChangeForm):
    """Customize PasswordChangeForm fields."""

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Restyle fields classes."""
        super().__init__(*args, **kwargs)
        fields = self.fields
        fields["old_password"].widget.attrs[
            "class"
        ] = "custom-input custom-input-height"
        fields["new_password1"].widget.attrs[
            "class"
        ] = "custom-input custom-input-height"
        fields["new_password2"].widget.attrs[
            "class"
        ] = "custom-input custom-input-height"
