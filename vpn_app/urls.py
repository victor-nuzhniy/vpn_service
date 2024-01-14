"""Urls for vpn_app."""
from django.urls import path, re_path

from vpn_app.views import (
    AccountView,
    CreateSiteLinkView,
    DeleteSiteLinkView,
    IndexView,
    UpdateSiteLinkView,
    VpnProxyView,
)

app_name = "vpn"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("create-site-link/", CreateSiteLinkView.as_view(), name="create_site_link"),
    path(
        "update-site-link/<int:owner_id>/<str:slug>/",
        UpdateSiteLinkView.as_view(),
        name="update_site_link",
    ),
    path(
        "delete-site-link/<int:owner_id>/<str:slug>/",
        DeleteSiteLinkView.as_view(),
        name="delete_site_link",
    ),
    path("account/<int:pk>/", AccountView.as_view(), name="account"),
    re_path(
        r"^localhost/(?P<path>([^/]+/?)*)$",  # noqa WPS360
        VpnProxyView.as_view(),
        name="vpn_local_view",
    ),
    re_path(r"(?P<path>.*)", VpnProxyView.as_view(), name="vpn_view"),  # noqa WPS360
]
