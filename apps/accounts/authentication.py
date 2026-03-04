from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        access = request.COOKIES.get("access")

        if not access:
            return None

        try:
            validated_token = self.get_validated_token(access)
        except (InvalidToken, TokenError):
            return None   # Ignore invalid tokens for public endpoints

        user = self.get_user(validated_token)

        return (user, validated_token)