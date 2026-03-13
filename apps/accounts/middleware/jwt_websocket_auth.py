from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token):
    """
    Get the user from the JWT access token.
    """
    try:
        access_token = AccessToken(token)
        user_id = access_token["user_id"]
        return User.objects.get(id=user_id)
    except (InvalidToken, TokenError, User.DoesNotExist):
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom middleware to authenticate WebSocket connections using JWT stored in cookies.
    """

    async def __call__(self, scope, receive, send):

        headers = dict(scope.get("headers", []))
        cookie_header = headers.get(b"cookie", b"")

        token = None

        if cookie_header:
            cookie_str = cookie_header.decode()

            cookies = cookie_str.split(";")

            for cookie in cookies:
                cookie = cookie.strip()

                if cookie.startswith("access="):
                    token = cookie.split("=", 1)[1]
                    break

        if token:
            scope["user"] = await get_user_from_token(token)
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)