"""Models for vpn_app."""
from django.contrib.auth.models import User
from django.db import models


class VpnSite(models.Model):
    """Model for site data."""

    name = models.CharField(max_length=100, verbose_name="Site name")
    url = models.URLField(verbose_name="Site url")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Site owner")
    used_links_number = models.BigIntegerField(
        default=0, verbose_name="Used links number"
    )
    sended_volume = models.BigIntegerField(default=0, verbose_name="Sended data volume")
    loaded_volume = models.BigIntegerField(default=0, verbose_name="Loaded data volume")

    def __str__(self) -> str:
        """Represent model."""
        return f"{self.name}"
