from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from google.oauth2 import id_token
from google.auth.transport import requests

from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.api.serializers.user_serializer import UserSerializer

User = get_user_model()


class GoogleAuthView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        token = request.data.get("token")

        if not token:
            return Response({"error": "Token required"}, status=400)

        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )

            email = idinfo["email"]
            name = idinfo.get("name")

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email,
                    "first_name": name
                }
            )

            refresh = RefreshToken.for_user(user)
            refresh["role"] = user.role

            response = Response({
                "user": UserSerializer(user).data
            })

            response.set_cookie(
                "access",
                str(refresh.access_token),
                httponly=True,
                secure=not settings.DEBUG,
                samesite="None",
                path="/",
            )

            response.set_cookie(
                "refresh",
                str(refresh),
                httponly=True,
                secure=not settings.DEBUG,
                samesite="None",
                path="/",
            )

            return response

        except ValueError:
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST
            )