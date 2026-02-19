from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from apps.accounts.api.serializers.cookie_refresh_serializer import CookieRefreshSerializer

User = get_user_model()

class RefreshView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=None,
        responses={200: dict, 401: dict},
        tags=["auth"],
        summary="Refresh access token using cookie",
        description="Uses refresh token from HTTP-only cookie and rotates tokens."
    )
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "No refresh token"},
                status=401
            )

        # Optional but fine for schema consistency
        serializer = CookieRefreshSerializer(
            data={"refresh": refresh_token}
        )
        serializer.is_valid(raise_exception=True)

        try:
            old_refresh = RefreshToken(refresh_token)

            user_id = old_refresh.get("user_id")
            if not user_id:
                raise TokenError("Invalid token payload")

            user = User.objects.get(id=user_id)

            # 🔥 THIS IS WHAT YOU MISSED
            old_refresh.blacklist()

            # ✅ CORRECT rotation
            new_refresh = RefreshToken.for_user(user)

        
        except (TokenError, User.DoesNotExist):
            response = Response(
                {"detail": "Invalid or expired refresh token"},
                status=401
            )
            response.delete_cookie("access", path="/", samesite="Lax")
            response.delete_cookie("refresh", path="/", samesite="Lax")
            return response

        response = Response({"detail": "Token refreshed"})

        response.set_cookie(
            "access",
            str(new_refresh.access_token),
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            path="/",
        )

        response.set_cookie(
            "refresh",
            str(new_refresh),
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            path="/",
        )

        return response
