from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
from session.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                # URLRouter just takes standard Django path() or url() entries.
                path("ws/session/", URLRouter(websocket_urlpatterns)),
            ]),
        )
    ),
})
