"""
ASGI config for agriculture_backend_app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from notification.consumers import BuyerConsumer,SellerConsumer
from django.core.asgi import get_asgi_application
from django.urls import path
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriculture_backend_app.settings')

django_asgi_app = get_asgi_application()
ws_patterns = [
    path('ws/buyer', BuyerConsumer.as_asgi()),
    path('ws/seller/', SellerConsumer.as_asgi()),
]
application= ProtocolTypeRouter({
    "http": django_asgi_app,
    'websocket':AuthMiddlewareStack(
        URLRouter(ws_patterns)
    )
})