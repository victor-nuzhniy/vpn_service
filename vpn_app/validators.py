"""Validators for vpn_app."""
import re

from django.core.exceptions import ValidationError


def validate_domain(value):
    """Check whether domain match sample."""
    if not re.match("[a-zA-Z0-9-:.]+", value):
        raise ValidationError("Try input a valid domain name.")
