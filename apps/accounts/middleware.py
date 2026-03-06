from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_string):
    try:
        # Validate the token
        access_token = AccessToken(token_string)
        # Fetch the user ID
        user_id = access_token["user_id"]
        # Retrieve the actual user record
        return User.objects.get(id=user_id)
    except (InvalidToken, TokenError, User.DoesNotExist):
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Extract headers from the scope to find cookies
        headers = dict(scope.get("headers", []))
        
        cookie_header = headers.get(b"cookie", b"").decode()
        
        access_token = None
        
        # Parse standard HTTP cookies
        if cookie_header:
            cookies = cookie_header.split("; ")
            for cookie in cookies:
                if cookie.startswith("access="):
                    access_token = cookie.split("=")[1]
                    break
        
        # If there's an access token, fetch the user asynchronously
        if access_token:
            scope["user"] = await get_user_from_token(access_token)
        else:
            scope["user"] = AnonymousUser()
            
        return await super().__call__(scope, receive, send)
