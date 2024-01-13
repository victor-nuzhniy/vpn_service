"""Validators for vpn_app."""
import re

from django.core.exceptions import ValidationError


def validate_domain(string_value: str) -> None:
    """Check whether domain match sample."""
    if not re.match("[a-zA-Z0-9-:.]+", string_value):
        raise ValidationError({"message": "Try input a valid domain name."})
