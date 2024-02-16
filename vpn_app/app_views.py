"""Views special for vpn_app."""
import typing

from django.http import Http404, HttpRequest, HttpResponseBase
from revproxy.utils import should_stream
from revproxy.views import ProxyView

from vpn_app import tasks
from vpn_app.app_services import ResponseDataModifier
from vpn_app.models import VpnSite


class BaseVpnProxyView(ProxyView):
    """Proxy view."""

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Rewrite __init__ method, add 'domain' attr."""
        self.domain: typing.Optional[str] = None
        super().__init__(*args, **kwargs)

    def dispatch(self, request: HttpRequest, path: str) -> HttpResponseBase:
        """Rewrite dispatch method. Add 'user_domain' cookie."""
        response = super().dispatch(request, path)
        response.set_cookie(key="user_domain", value=self.domain)
        return response

    def get_quoted_path(self, path: str) -> str:
        """Rewrite get_quoted_path method, hook for perform_additional_operations."""
        path = super().get_quoted_path(path)
        return self.perform_additional_operations(path)

    def perform_additional_operations(self, path: str) -> str:
        """
        Check whether user is login and path content.

        If path starts with 'localhost', get domain, otherwise get it from cookies.
        If not domain or user is anonimous - raise 404.
        Try to get VpnSite instance and if it is, set upstream property, otherwise
        raise 404.
        In case of 'localhost' present in path, clean it.
        Return path (modified or not).
        """
        req_path: str = self.request.path
        if req_path.startswith("/localhost") or req_path.startswith("localhost"):
            path_list = req_path.split("localhost")
            path = path_list[-1]
            path_list = path.split("/")
            self.domain = path_list[1]
            path = "/".join(path_list[2:])
        else:
            self.domain = self.request.COOKIES.get("user_domain")
        if not self.domain or self.request.user.is_anonymous:
            raise Http404
        vpn_site: typing.Optional[VpnSite] = VpnSite.objects.filter(
            owner=self.request.user,
            domain__startswith=self.domain,
        ).first()
        if not vpn_site:
            raise Http404

        self.upstream = "{scheme}://{domain}".format(
            scheme=vpn_site.scheme,
            domain=self.domain,
        )
        if self.request.path.startswith("/localhost"):
            tasks.add_links_number.delay(self.request.user.id, self.domain)
        volume = self.request.headers.get("Content-Length", 0)
        if volume:
            tasks.add_loaded_volume.delay(self.request.user.id, self.domain, volume)
        return path

    def _created_proxy_response(
        self,
        request: HttpRequest,
        path: str,
    ) -> HttpResponseBase:
        """Add functionality to method."""
        response = super()._created_proxy_response(request, path)
        self._set_content_type(request, response)
        content_length = response.headers.get("Content-Length", 0)
        if content_length:
            tasks.add_sended_volume.delay(request.user.id, self.domain, content_length)
        if not should_stream(response) and self.domain:
            ResponseDataModifier(
                response,
                request.get_host(),
                self.domain,
            ).modify_response()
        set_cookie: str = response.headers.get('Set-Cookie')
        if set_cookie:
            new_cookie = ""
            for cookie in set_cookie.split("; "):
                if not cookie.startswith("Max-Age"):
                    new_cookie += cookie
            response.headers["Set-Cookie"] = new_cookie
        return response

    def _replace_host_on_redirect_location(
        self,
        request: HttpRequest,
        proxy_response: HttpResponseBase,
    ) -> None:
        """Rewrite method to modify links with given domain name."""
        super()._replace_host_on_redirect_location(request, proxy_response)
        location = proxy_response.headers.get("Location")
        if location:
            if request.is_secure():
                scheme = "https://"
            else:
                scheme = "http://"
            request_host = "{scheme}{host}/localhost/{domain}".format(
                scheme=scheme,
                host=request.get_host(),
                domain=self.domain,
            )
            if location.startswith("http"):
                upstream_host_http = "http://{host}".format(
                    host=self._parsed_url.netloc,
                )
                upstream_host_https = "https://{host}".format(
                    host=self._parsed_url.netloc,
                )
                location = location.replace(upstream_host_http, request_host)
                location = location.replace(upstream_host_https, request_host)
            else:
                location = request_host + location
            proxy_response.headers["Location"] = location
            self.log.debug(
                "Proxy response LOCATION: {header}".format(
                    header=proxy_response.headers["Location"],
                ),
            )
