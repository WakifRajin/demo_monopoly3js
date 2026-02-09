from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from monopoly import consumers

# Channels 2.x uses URLRouter with path/url patterns
application = ProtocolTypeRouter({
    "websocket": URLRouter([
        # This maps all WebSocket connections to your message handler
        path("monopoly/", consumers.MonopolyConsumer.as_asgi()),
    ]),
})