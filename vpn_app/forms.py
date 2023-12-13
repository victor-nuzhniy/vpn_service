"""Forms for vpn_app."""
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


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
