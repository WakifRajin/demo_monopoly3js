from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from monopoly import consumers

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter([
            # Removed .as_asgi() from the end of consumers.MonopolyConsumer
            re_path(r'(?:monopoly/)?(?P<mode>\w+)/(?P<room_name>\w+)/?$', consumers.MonopolyConsumer),
        ])
    ),
})