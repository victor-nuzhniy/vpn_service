"""Urls for vpn_app."""
from django.contrib.auth.views import LogoutView
from django.urls import path

from vpn_app.views import (
    CreateSiteLinkView,
    CustomLoginView,
    CustomPasswordChangeView,
    IndexView,
    RegisterView,
)

app_name = "vpn"

urlpatterns = [
    path("", IndexView.as_view(), name="vpn"),
    path("sign-up/", RegisterView.as_view(), name="sign_up"),
    path("sign-in/", CustomLoginView.as_view(), name="sign_in"),
    path(
        "password-change/", CustomPasswordChangeView.as_view(), name="password_change"
    ),
    path("logout/", LogoutView.as_view(next_page="vpn:index"), name="logout"),
    path("create-site-link/", CreateSiteLinkView.as_view(), name="create_site_link"),
]
