from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/notify/(?P<room_name>\w+)/$", consumers.NotificationConsumer.as_asgi()),
    re_path(r"ws/book-slot/(?P<event_room_name>\w+)/$", consumers.EventConsumer.as_asgi()),
]