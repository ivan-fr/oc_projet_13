from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.conf.urls import url
from session.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                # URLRouter just takes standard Django path() or url() entries.
                url(r'^ws/session/$', URLRouter(websocket_urlpatterns)),
            ]),
        )
    ),
})
