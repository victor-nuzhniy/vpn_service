"""Urls for vpn_app."""
from django.contrib.auth.views import LogoutView
from django.urls import path

from vpn_app.views import (
    AccountView,
    CreateSiteLinkView,
    CustomLoginView,
    CustomPasswordChangeView,
    DeleteSiteLinkView,
    IndexView,
    RegisterView,
    UpdateSiteLinkView,
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
]
