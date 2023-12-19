"""Utilities for vpn_app."""
from __future__ import annotations

import os
import re
from typing import Any, Optional
from urllib.request import urlopen

import bs4
from urllib3 import BaseHTTPResponse


class Config:
    """Class for storing configurational data."""

    public_ip: Optional[str] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> Config:
        """Create new instance, if it's None, otherwise use earlier created one."""
        if not hasattr(cls, "instance"):
            cls.instance = super(Config, cls).__new__(cls, *args, **kwargs)
            if public_ip := str(os.getenv("HOST")):
                cls.instance.__dict__["public_ip"] = public_ip
            else:
                cls.instance.__dict__["public_ip"] = cls.get_public_ip()
        return cls.instance

    def get_var(self, name: str) -> Any:
        """Get config value by name."""
        return self.__dict__.get(name)

    @staticmethod
    def get_public_ip() -> str:
        """Get public ip."""
        return urlopen("https://ident.me").read().decode("utf8")


def find_sample(sample, *words, **kwords) -> bool:
    """Define if sample satisfy the case."""
    return (
        sample
        and all([re.compile(word).search(sample) for word in words])
        and all([re.compile(word).search(sample) for word in kwords.values()])
    )


def find_sample_without_word(sample, *words) -> bool:
    """Define if sample satisfy the case."""
    return sample and all([not re.compile(word).search(sample) for word in words])


def modify_response(response: BaseHTTPResponse, host: str, domain: str) -> None:
    """Modify response: find links and replace them."""
    xsoup = bs4.BeautifulSoup(response.data or b"", "html.parser")
    for elem in xsoup.find_all(
        "a",
        href=lambda x: find_sample_without_word(
            x, "http", "localhost", "#", "mailto", "tel:"
        ),
    ):
        if elem["href"].startswith("/"):
            elem["href"] = f"http://{host}/localhost/{domain}/{elem['href'][1:]}"
        else:
            elem["href"] = f"http://{host}/localhost/{domain}/{elem['href']}"
    find_links_tag = xsoup.find("script", atr="find-links")
    if not find_links_tag:
        with open("vpn_app/admin_static_files/vpn_app/js/find_link.js", "r") as f:
            file_content = f.read()
        body = xsoup.find("body")
        if body:
            find_links_tag = xsoup.new_tag("script", atr="find-links")
            find_links_tag.append(file_content)
            body.append(find_links_tag)

    for elem in xsoup.find_all(
        "form",
        action=lambda x: find_sample_without_word(x, "http", "localhost"),
    ):
        if elem["action"].startswith("/"):
            elem["action"] = f"http://{host}/localhost/{domain}/{elem['action'][1:]}"
        else:
            elem["action"] = f"http://{host}/localhost/{domain}/{elem['action']}"
    response._body = xsoup.prettify()
