import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

from apps.accounts.middleware.jwt_websocket_auth import JWTAuthMiddleware
from apps.notifications.routing import websocket_urlpatterns

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,

        "websocket":JWTAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        ),
    }
)