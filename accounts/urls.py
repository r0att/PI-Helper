from django.urls import path

from .views import (
    login_view,
    logout_view,
    register,
    verify_email,
    profile,
    confirm_password_change,
    change_password,
    check_username,
)


urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("verify/<uuid:token>/", verify_email, name="verify_email"),
    path("profile/", profile, name="profile"),
    path("change-password/", change_password, name="change_password"),
    path("confirm-password-change/<uuid:token>/", confirm_password_change, name="confirm_password_change"),
    path("check-username/", check_username, name="check_username")
]