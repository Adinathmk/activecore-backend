from django.urls import path
from   apps.accounts.api.views.public.login_view import LoginView
from  apps.accounts.api.views.public.refresh_token import RefreshView
from  apps.accounts.api.views.public.logout_view import LogoutView
from  apps.accounts.api.views.public.register_view import RegisterView
from .views.admin.admin_user_action import (
    AdminUserBlockToggleView,
    AdminUserDeleteView
)
from .views.admin.admin_user_list import AdminUserListView
from .views.admin.admin_user_detail import AdminUserDetailView
from .views.public.me_view import MeView
from .views.public.otp_view import VerifyOTPView,SendOTPView,ResetPasswordView,ForgotPasswordView

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("refresh/", RefreshView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("forgot-password/", ForgotPasswordView.as_view()),
    path("reset-password/", ResetPasswordView.as_view()),


    
    path("send-otp/", SendOTPView.as_view()),
    path("verify-otp/", VerifyOTPView.as_view()),
    path("me/", MeView.as_view(), name="me"),
    


    path("admin/users/", AdminUserListView.as_view()),
    path("admin/users/<uuid:pk>/", AdminUserDetailView.as_view()),
    path("admin/users/<uuid:pk>/block/", AdminUserBlockToggleView.as_view()),
    path("admin/users/<uuid:pk>/delete/", AdminUserDeleteView.as_view()),
]
