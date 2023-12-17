"""Utilities for vpn_app."""
from __future__ import annotations

import re
from typing import Any, Optional
from urllib.request import urlopen

from django.contrib.auth.models import User
from django.db.models import F

from vpn_app.models import VpnSite


class Config:
    """Class for storing configurational data."""

    public_ip: Optional[str] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> Config:
        """Create new instance, if it's None, otherwise use earlier created one."""
        if not hasattr(cls, "instance"):
            cls.instance = super(Config, cls).__new__(cls, *args, **kwargs)
            cls.instance.__dict__["public_ip"] = cls.get_public_ip()
        return cls.instance

    def get_var(self, name: str) -> Any:
        """Get config value by name."""
        return self.__dict__.get(name)

    @staticmethod
    def get_public_ip() -> str:
        """Get public ip."""
        return urlopen("https://ident.me").read().decode("utf8")


def find_sample(sample, word) -> bool:
    """Define if sample satisfy the case."""
    return sample and re.compile(word).search(sample)


def find_sample_without_word(sample, word) -> bool:
    """Define if sample satisfy the case."""
    return sample and not re.compile(word).search(sample)


def add_links_number(vpn_site: VpnSite) -> None:
    """Increase used_links_number model field."""
    vpn_site.used_links_number = F("used_links_number") + 1
    vpn_site.save()


def add_loaded_volume(vpn_site: VpnSite, volume: str | int) -> None:
    """Increase loaded_volume model field."""
    vpn_site.loaded_volume = F("loaded_volume") + int(volume)
    vpn_site.save()


def add_sended_volume(
    user: User, domain: str, volume: str | int, volume_upper: str | int
) -> None:
    """Increase loaded_volume model field."""
    vpn_site = VpnSite.objects.filter(owner=user, domain=domain).first()
    vpn_site.sended_volume = F("sended_volume") + int(volume) + int(volume_upper)
    vpn_site.save()
