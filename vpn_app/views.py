"""Views for vpn_app."""
from django.http import HttpResponse
from django.views import View
from django.views.generic import TemplateView


class IndexView(TemplateView):
    """Index view."""

    template_name = "vpn_app/index.html"
    extra_context = {"title": "Welcome"}


class VpnView(View):
    """Vpn view."""

    def get(self, request, *args, **kwargs):
        """Handle get request."""
        return HttpResponse("Hello World!")
