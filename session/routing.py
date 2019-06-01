from django.urls import path, re_path

from session import consumers

websocket_urlpatterns = [
    re_path(r'^whoisonline/(?P<askmanifest>[0|1]+)$', consumers.WhoIsOnlineConsumer),
    re_path(r'^thread/(?P<username>[\w.@+-]+)$', consumers.ThreadConsumer),
    re_path(r'^whoisonlinethread/(?P<onthreadpage>[0|1]+)$', consumers.WhoIsOnlineThreadConsumer)
]
