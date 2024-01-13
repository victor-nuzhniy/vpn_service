"""Urls for auth_app."""
from django.contrib.auth.views import LogoutView
from django.urls import path

from auth_app.views import CustomLoginView, CustomPasswordChangeView, RegisterView

app_name = "auth"

urlpatterns = [
    path("sign-up/", RegisterView.as_view(), name="sign_up"),
    path("sign-in/", CustomLoginView.as_view(), name="sign_in"),
    path(
        "password-change/",
        CustomPasswordChangeView.as_view(),
        name="password_change",
    ),
    path("logout/", LogoutView.as_view(next_page="vpn:index"), name="logout"),
]
