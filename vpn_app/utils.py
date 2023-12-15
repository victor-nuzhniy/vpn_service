"""Utilities for vpn_app."""
from __future__ import annotations

import re
from typing import Any, Optional
from urllib.request import urlopen


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
