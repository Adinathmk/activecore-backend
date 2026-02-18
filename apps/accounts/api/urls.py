from django.urls import path
from   apps.accounts.api.views.public.login_view import LoginView
from  apps.accounts.api.views.public.refresh_token import RefreshView
from  apps.accounts.api.views.public.logout_view import LogoutView
from  apps.accounts.api.views.public.register_view import RegisterView

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("refresh/", RefreshView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("register/", RegisterView.as_view(), name="auth-register"),
]
