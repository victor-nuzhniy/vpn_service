"""Models for vpn_app."""
from django.contrib.auth.models import User
from django.db import models

from vpn_app.validators import validate_domain


class VpnSite(models.Model):
    """Model for site data."""

    schemes = [("http", "http"), ("https", "https")]

    name = models.CharField(max_length=100, verbose_name="Site name")
    domain = models.CharField(
        max_length=200,
        validators=[validate_domain],
        verbose_name="Site domain",
    )
    scheme = models.CharField(
        max_length=20,
        choices=schemes,
        default="http",
        verbose_name="Scheme",
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Site owner")
    used_links_number = models.BigIntegerField(
        default=0,
        verbose_name="Used links number",
    )
    sended_volume = models.BigIntegerField(default=0, verbose_name="Sended data volume")
    loaded_volume = models.BigIntegerField(default=0, verbose_name="Loaded data volume")

    def __str__(self) -> str:
        """Represent model."""
        return str(self.name)
