# routing.py
from django.urls import path
from .consumers import WaiterConsumer

websocket_urlpatterns = [
    path('ws/waiters/', WaiterConsumer.as_asgi()),
]
