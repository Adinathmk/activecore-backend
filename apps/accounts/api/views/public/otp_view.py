from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse

from rest_framework_simplejwt.tokens import RefreshToken

from ....models import UserOTP
from ...serializers.otp_serializer import VerifyOTPSerializer,SendOTPSerializer,ForgotPasswordSerializer,ResetPasswordSerializer
from ....utils import create_and_send_otp
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
import logging

logger = logging.getLogger(__name__)


User = get_user_model()


# ======================================
# 🔹 Send OTP
# ======================================

class SendOTPView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @extend_schema(
        summary="Send Email Verification OTP",
        tags=["auth"],
        request=SendOTPSerializer,
        responses={
            200: OpenApiResponse(description="OTP sent successfully"),
            400: OpenApiResponse(description="Invalid request"),
        },
    )
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.warning(f"OTP request for non-existent email: {email}")
            return Response({"error": "User not found"}, status=404)

        if user.is_verified:
            return Response(
                {"message": "Account already verified"},
                status=200
            )

        # ✅ Always email
        create_and_send_otp(user, otp_type="verify", channel="email")
        logger.info(f"Verification OTP sent to {email}")

        return Response(
            {"message": "Verification OTP sent via email"},
            status=200
        )


# ======================================
# 🔹 Verify OTP + Auto Login
# ======================================

class VerifyOTPView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @extend_schema(
        summary="Verify Email OTP",
        tags=["auth"],
        request=VerifyOTPSerializer,
        responses={
            200: OpenApiResponse(description="Account verified & logged in"),
            400: OpenApiResponse(description="Invalid or expired OTP"),
        },
    )
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
            UserOTP.objects
            .filter(
                user=user,
                otp_type="verify",
                channel="email",  # 🔥 fixed
                is_used=False
            )
            .order_by("-created_at")
            .first()
        )

        if not otp_obj:
            return Response({"error": "No OTP found"}, status=400)

        if otp_obj.is_expired():
            return Response({"error": "OTP expired"}, status=400)

        if otp_obj.attempts >= 5:
            logger.warning(f"Too many OTP verification attempts for user: {email}")
            otp_obj.delete()
            return Response({"error": "Too many attempts"}, status=400)

        if not check_password(otp_input, otp_obj.otp_hash):
            otp_obj.attempts += 1
            otp_obj.save()
            return Response({"error": "Invalid OTP"}, status=400)

        user.is_verified = True
        user.save()
        logger.info(f"User {email} verified successfully via OTP.")

        otp_obj.is_used = True
        otp_obj.save()

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        response = Response(
            {"message": "Account verified successfully"},
            status=200
        )

        response.set_cookie(
            key="access_token",
            value=str(access_token),
            httponly=True,
            secure=False,  # True in production
            samesite="None",
        )

        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite="None",
        )

        return response
    

class ForgotPasswordView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @extend_schema(
        summary="Request Password Reset OTP",
        description="Sends OTP via email or WhatsApp.",
        tags=["auth"],
        request=ForgotPasswordSerializer,
        responses={
            200: OpenApiResponse(description="OTP sent successfully"),
        },
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        email = serializer.validated_data["email"]
        channel = serializer.validated_data["channel"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"message": "If account exists, OTP sent"},
                status=200
            )

        create_and_send_otp(
            user,
            otp_type="reset",
            channel=channel
        )
        logger.info(f"Password reset OTP sent to {email} via {channel}")

        return Response(
            {"message": f"Reset OTP sent via {channel}"},
            status=200
        )

class ResetPasswordView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @extend_schema(
        summary="Reset Password using OTP",
        tags=["auth"],
        request=ResetPasswordSerializer,
        responses={
            200: OpenApiResponse(description="Password reset successful"),
            400: OpenApiResponse(description="Invalid or expired OTP"),
        },
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        email = serializer.validated_data["email"]
        otp_input = serializer.validated_data["otp"]
        new_password = serializer.validated_data["new_password"]
        channel = serializer.validated_data["channel"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=400)

        otp_obj = (
            UserOTP.objects
            .filter(
                user=user,
                otp_type="reset",
                channel=channel,
                is_used=False
            )
            .order_by("-created_at")
            .first()
        )

        if not otp_obj or otp_obj.is_expired():
            return Response({"error": "Invalid or expired OTP"}, status=400)

        if not check_password(otp_input, otp_obj.otp_hash):
            otp_obj.attempts += 1
            otp_obj.save()

            if otp_obj.attempts >= 5:
                otp_obj.delete()
                return Response({"error": "Too many attempts"}, status=400)

            return Response({"error": "Invalid OTP"}, status=400)

        user.set_password(new_password)
        user.save()
        logger.info(f"Password reset successful for user {email}")

        for token in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=token)

        otp_obj.delete()

        return Response(
            {"message": "Password reset successful"},
            status=200
        )