from django.urls import path
from .views.login_view import LoginView
from .views.refresh_token import RefreshView
from .views.logout_view import LogoutView
from apps.accounts.views.register_view import RegisterView

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("refresh/", RefreshView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("register/", RegisterView.as_view(), name="auth-register"),
]
