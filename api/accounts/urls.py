from django.urls import path, include
from rest_auth.views import (
    LoginView,
    LogoutView,
    UserDetailsView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView,
)

urlpatterns = [
    path("login", LoginView.as_view(), name="rest_login"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("password/reset", PasswordResetView.as_view(), name="rest_password_reset"),
    path("user", UserDetailsView.as_view(), name="user"),
    path("password/change", PasswordChangeView.as_view(), name="rest_password_change"),
    path("password/reset", PasswordResetView.as_view(), name="rest_password_reset"),
    path("password/reset/confirm", PasswordResetConfirmView.as_view(), name="rest_password_reset_confirm"),
    path("register", include("rest_auth.registration.urls")),
]
