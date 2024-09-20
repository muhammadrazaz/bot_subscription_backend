from django.urls import path
from instagram import consumer


websocket_urlpatterns = [
    # path('ws/sc/', consumer.MySyncConsumer.as_asgi()),
    path('ws/ac/', consumer.MyAsyncConsumer.as_asgi()),
]