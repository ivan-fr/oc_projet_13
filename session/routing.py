from django.urls import path, re_path

from session import consumers

websocket_urlpatterns = [
    re_path(r'whoisonline/(?P<thread>[1|0]+)$', consumers.WhoIsOnlineConsumer),
    re_path(r'^thread/(?P<username>[\w.@+-]+)$', consumers.ThreadConsumer)
]
