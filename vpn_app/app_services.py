"""Utilities for vpn_app."""
from __future__ import annotations

import re

import bs4
from urllib3 import HTTPResponse


class ResponseDataModifier(object):
    """Class with response data modification logic."""

    def __init__(self, response: HTTPResponse, host: str, domain: str) -> None:
        """Initialize class instance."""
        self.response = response
        self.xsoup = bs4.BeautifulSoup(response.data or b"", "html.parser")
        self.host = host
        self.domain = domain

    def is_word_not_in_sample(self, word: str, sample: str) -> bool:
        """Define whether word in sample."""
        return not re.compile(word).search(sample)

    def find_sample_without_word(self, sample: str, *words: str) -> bool:
        """Define if sample satisfy the case."""
        return bool(sample) and all(
            self.is_word_not_in_sample(word, sample) for word in words
        )

    def modify_xsoup_with_tag_and_attr(
        self,
        tag_name: str,
        tag_attr: str,
        *restrictions: str,
    ) -> None:
        """Modify data with tag_name and attr name, using restrictions, if any."""
        tags = self.xsoup.find_all(
            tag_name,
            href=lambda elem: self.find_sample_without_word(elem, *restrictions),
        )
        for tag in tags:
            if tag[tag_attr].startswith("/"):
                element = tag[tag_attr][1:]
            else:
                element = tag[tag_attr]
            tag[tag_attr] = "http://{host}/localhost/{domain}/{elem}".format(
                host=self.host,
                domain=self.domain,
                elem=element,
            )

    def add_script(self, attr: str) -> None:
        """Add script to data, if script havn't already exist."""
        find_links_tag = self.xsoup.find("script", atr=attr)
        if not find_links_tag:
            with open(
                "vpn_app/admin_static_files/vpn_app/js/find_link.js",
                "r",
            ) as file_data:
                file_content = file_data.read()
            body = self.xsoup.find("body")
            if body:
                find_links_tag = self.xsoup.new_tag("script", atr=attr)
                find_links_tag.append(file_content)
                body.append(find_links_tag)

    def modify_response(self) -> None:
        """Modify response: find links and replace them."""
        self.modify_xsoup_with_tag_and_attr(
            "a",
            "href",
            "http",
            "localhost",
            "#",
            "mailto",
            "tel:",
        )
        self.add_script("find-links")
        self.modify_xsoup_with_tag_and_attr("form", "action", "http", "localhost")
        self.response._body = self.xsoup.prettify()  # noqa WPS437
