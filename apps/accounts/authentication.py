from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        access = request.COOKIES.get("access")
        
        if not access:
            return None

        validated_token = self.get_validated_token(access)
        return self.get_user(validated_token), validated_token
