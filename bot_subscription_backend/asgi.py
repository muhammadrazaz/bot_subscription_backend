
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot_subscription_backend.settings')
import django
django.setup()
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import os
import instagram.routing
from auth_app.middleware import TokenAuthMiddleware
from channels.security.websocket import AllowedHostsOriginValidator

# application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        TokenAuthMiddleware(  # Applying your custom Token Authentication middleware
        URLRouter(
            instagram.routing.websocket_urlpatterns  # Using WebSocket URL patterns from your routing file
        )
    )
    ),
})