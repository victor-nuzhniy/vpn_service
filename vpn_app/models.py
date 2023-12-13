"""Models for vpn_app."""
from django.db import models


class VpnSite(models.Model):
    """Model for site data."""

    name = models.CharField(max_length=100, verbose_name="Site name")
    url = models.URLField(verbose_name="Site url")
    used_links_number = models.BigIntegerField(verbose_name="Used links number")
    sended_volume = models.BigIntegerField(verbose_name="Sended data volume")
    loaded_volume = models.BigIntegerField(verbose_name="Loaded data volume")

    def __str__(self) -> str:
        """Represent model."""
        return f"{self.name}"
