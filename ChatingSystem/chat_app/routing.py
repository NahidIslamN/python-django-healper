from django.urls import path
from .consumers import *


websocket_urlpatterns = [
    path(r'ws/asc/chat/<int:chat_id>/', ChatConsumer.as_asgi()),
    path(r'ws/asc/reaction/<int:message_id>/', Sent_Reaction_ON_Message.as_asgi()),
    path(r"ws/asc/call/<int:room_name>/", CallConsumer.as_asgi()),
    path(r'ws/asc/chat/seen_status_update/<int:chat_id>/', MessageSeenStatusUpdate.as_asgi()),
]
