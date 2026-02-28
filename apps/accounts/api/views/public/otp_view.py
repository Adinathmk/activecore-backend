from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse

from rest_framework_simplejwt.tokens import RefreshToken

from ....models import EmailOTP
from ...serializers.otp_serializer import VerifyOTPSerializer,SendOTPSerializer,ForgotPasswordSerializer,ResetPasswordSerializer
from ....utils import create_and_send_otp
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken


User = get_user_model()


# ======================================
# 🔹 Send OTP
# ======================================

@extend_schema(
    summary="Send Email OTP",
    tags=["auth"],
    request=SendOTPSerializer,
    responses={
        200: OpenApiResponse(description="OTP sent successfully"),
        400: OpenApiResponse(description="Invalid email"),
    },
)
class SendOTPView(APIView):
    authentication_classes = [] 
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=404
            )

        if user.is_verified:
            return Response(
                {"message": "Account already verified"},
                status=200
            )

        create_and_send_otp(user)

        return Response(
            {"message": "OTP sent successfully"},
            status=200
        )


# ======================================
# 🔹 Verify OTP + Auto Login
# ======================================

@extend_schema(
    summary="Verify Email OTP",
    tags=["auth"],
    request=VerifyOTPSerializer,
    responses={
        200: OpenApiResponse(description="Account verified & logged in"),
        400: OpenApiResponse(description="Invalid or expired OTP"),
    },
)
class VerifyOTPView(APIView):
    authentication_classes = [] 
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        email = serializer.validated_data["email"]
        otp_input = serializer.validated_data["otp"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=400)

        otp_obj = (
            EmailOTP.objects
            .filter(user=user, is_used=False)
            .order_by("-created_at")
            .first()
        )

        if not otp_obj:
            return Response({"error": "No OTP found"}, status=400)

        if otp_obj.is_expired():
            return Response({"error": "OTP expired"}, status=400)

        if otp_obj.attempts >= 5:
            return Response({"error": "Too many attempts"}, status=400)

        if not check_password(otp_input, otp_obj.otp_hash):
            otp_obj.attempts += 1
            otp_obj.save()
            return Response({"error": "Invalid OTP"}, status=400)

        # ✅ Activate account
        user.is_verified = True
        user.save()

        otp_obj.is_used = True
        otp_obj.save()

        # 🔐 Generate JWT Tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        response = Response(
            {"message": "Account verified successfully"},
            status=200
        )

        # 🍪 Set HttpOnly cookies
        response.set_cookie(
            key="access_token",
            value=str(access_token),
            httponly=True,
            secure=False,  # Change to True in production (HTTPS)
            samesite="Lax",
        )

        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,  # Change to True in production
            samesite="Lax",
        )

        return response
    

@extend_schema(
    summary="Request password reset OTP",
    description="Sends an OTP to the user's email for password reset.",
    tags=["auth"],
    request=ForgotPasswordSerializer,
    responses={
        200: OpenApiResponse(description="OTP sent successfully"),
        400: OpenApiResponse(description="Invalid request"),
    },
)
class ForgotPasswordView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "If email exists, OTP sent"}, status=200)

        create_and_send_otp(user, otp_type="reset")

        return Response({"message": "OTP sent to email"}, status=200)
    



@extend_schema(
    summary="Reset password using OTP",
    description="Verifies OTP and sets a new password. Logs out all active sessions.",
    tags=["auth"],
    request=ResetPasswordSerializer,
    responses={
        200: OpenApiResponse(description="Password reset successful"),
        400: OpenApiResponse(description="Invalid OTP or expired OTP"),
    },
)
class ResetPasswordView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp_input = request.data.get("otp")
        new_password = request.data.get("new_password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=400)

        otp_obj = EmailOTP.objects.filter(
            user=user,
            otp_type="reset",
            is_used=False
        ).order_by("-created_at").first()

        if not otp_obj or otp_obj.is_expired():
            return Response({"error": "Invalid or expired OTP"}, status=400)

        if not check_password(otp_input, otp_obj.otp_hash):
            return Response({"error": "Invalid OTP"}, status=400)

        # ✅ Set new password
        user.set_password(new_password)
        user.save()

        # 🔥 Blacklist all existing refresh tokens
        for token in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=token)

        # ✅ Delete OTP
        otp_obj.delete()

        return Response({"message": "Password reset successful"}, status=200)