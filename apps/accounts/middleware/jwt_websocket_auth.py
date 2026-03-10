from urllib.parse import parse_qs
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()


class JWTAuthMiddleware(BaseMiddleware):

    async def __call__(self, scope, receive, send):
        query_string = scope["query_string"].decode()
        query_params = parse_qs(query_string)
        
        
        token = None
        query_token = query_params.get("token")
        if query_token:
            token = query_token[0].strip()
        
       
        if not token or token == "undefined":
            headers = dict(scope.get("headers", []))
            cookie_bytes = headers.get(b"cookie", b"")
            cookie_header = cookie_bytes.decode()
            if cookie_header:
                for cookie in cookie_header.split(";"):
                    parts = cookie.strip().split("=", 1)
                    if len(parts) == 2 and parts[0] == "access":
                        token = parts[1]
                        print("WebSocket Auth: Using token from cookie")
                        break

       
        if token and token != "undefined":
            if token.startswith('Bearer '):
                token = token[7:]
            
           
            t_len = len(token)
            t_start = token[:10] if t_len > 10 else token
            t_end = token[-10:] if t_len > 10 else ""
            print(f"WebSocket Auth: Received token (length {t_len}): {t_start}...{t_end}")
            
            try:
                access_token = AccessToken(token)
                user_id = access_token["user_id"]
                user = await self.get_user(user_id)
                scope["user"] = user
                
                if user.is_authenticated:
                    print(f"WebSocket Auth: Success for user {user.email}")
                else:
                    print(f"WebSocket Auth: User found but not authenticated: {user}")

            except (InvalidToken, TokenError) as e:
                print(f"WebSocket Auth: Invalid token - {str(e)}")
                scope["user"] = AnonymousUser()
            except Exception as e:
                print(f"WebSocket Auth: Unexpected error - {str(e)}")
                scope["user"] = AnonymousUser()
        else:
            print("WebSocket Auth: No token provided in query or cookie")
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):

        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()