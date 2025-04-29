import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import app.routing  # assuming your app is named `app`
from django.core.asgi import get_asgi_application
import app.routing as routing



os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket" : AuthMiddlewareStack(
            URLRouter(
                routing.websocket_urlpatterns
            ) 
    )
})
