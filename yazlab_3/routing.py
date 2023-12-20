# routing.py
from django.urls import path
from .consumers import WaiterConsumer,ChefConsumer,TableConsumer,CashConsumer
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

websocket_urlpatterns = [
    path('ws/waiter/', WaiterConsumer.as_asgi()),
    path('ws/chef/', ChefConsumer.as_asgi()),
    path('ws/table/', TableConsumer.as_asgi()),
    path('ws/cashRegister/', CashConsumer.as_asgi()),

]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})