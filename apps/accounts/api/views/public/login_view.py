from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from apps.accounts.api.serializers.login_serializer import LoginSerializer
from apps.accounts.api.serializers.user_serializer import UserSerializer
import logging

logger = logging.getLogger(__name__)

from drf_spectacular.utils import extend_schema

class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=LoginSerializer,
        responses={200: dict},
        tags=["auth"],
    )

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        refresh["role"] = user.role

        logger.info(f"User {user.email} (ID: {user.id}) logged in successfully.")

        response = Response({
            "user": UserSerializer(user).data
        })

        response.set_cookie(
            "access",
            str(refresh.access_token),
            httponly=True,
            secure=True,
            samesite="None",
            path="/",
        )

        response.set_cookie(
            "refresh",
            str(refresh),
            httponly=True,
            secure=True,
            samesite="None",
            path="/",
        )
        return response