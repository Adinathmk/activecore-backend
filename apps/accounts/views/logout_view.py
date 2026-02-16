from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.conf import settings

class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh")

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                # Token already invalid or expired
                pass

        response = Response({"detail": "Logged out successfully"})

        response.delete_cookie(
            "access",
            path="/",
            samesite="Lax",
        )
        response.delete_cookie(
            "refresh",
            path="/",
            samesite="Lax",
        )

        return response
