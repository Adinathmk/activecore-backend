import os

# 1. Set Django settings first
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

# 2. Now safe to import Django-dependent modules
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from apps.accounts.middleware.jwt_websocket_auth import JWTAuthMiddleware
from apps.notifications.routing import websocket_urlpatterns as notification_ws
from apps.chat.routing import websocket_urlpatterns as chat_ws


# Combine websocket routes
websocket_urlpatterns = notification_ws + chat_ws

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        )
    ),
})