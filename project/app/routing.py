from django.urls import re_path
from . import consumers 
from channels.routing import ProtocolTypeRouter , URLRouter
from channels.auth import AuthMiddlewareStack


websocket_urlpatterns = [
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
    re_path("ws/private-chat/<int:user_id>/", consumers.PrivateChatConsumer.as_asgi()),

]



application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})