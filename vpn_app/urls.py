"""Urls for vpn_app."""
from django.urls import path

from vpn_app.views import IndexView, RegisterView

app_name = "vpn"

urlpatterns = [
    path("", IndexView.as_view(), name="vpn"),
    path("sign-up/", RegisterView.as_view(), name="sign_up"),
]
