"""Admin site configuration for vpn_app."""
from django.contrib import admin

from vpn_app.models import VpnSite


class VpnSiteAdmin(admin.ModelAdmin):
    """VpnSite model admin site configuration."""

    model = VpnSite
    list_display = (
        "id",
        "name",
        "domain",
        "used_links_number",
        "sended_volume",
        "loaded_volume",
    )
    list_display_links = ("id", "name", "domain")


admin.site.register(VpnSite, VpnSiteAdmin)
