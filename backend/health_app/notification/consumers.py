from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from urllib.parse import parse_qs
import jwt
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from user.models import User
class BuyerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = self.scope["query_string"].decode() 
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]
        self.room_name = 'health_data_buyer'
        self.room_group_name = 'health_data_buyer_group'
        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                self.scope["user"] = await self.get_user(payload["user_id"])
            except Exception as e:
                self.scope["user"] = AnonymousUser()
                await self.close(code=4001) 
        else:
            self.scope["user"] = AnonymousUser()
            await self.close(code=4002)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def receive(self, text_data):
        await self.send(text_data=json.dumps({
            'status': 'got your message'
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def broadcast_message(self, event):
        user_id=event['user_id']
        message = event['data']
        if self.scope['user'] and str(self.scope['user'].user_id) != str(user_id):
            await self.send(text_data=json.dumps(message))

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(user_id=user_id)
    
class SellerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        headers = dict(self.scope["headers"])
        token_header = headers.get(b"authorization", None)
        self.room_name = 'health_data_seller'
        self.room_group_name = 'health_data_seller_group'
        if token_header:
            try:
                token = token_header.decode().split(" ")[1]
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                self.scope["user"] = await self.get_user(payload["user_id"])
            except Exception as e:
                self.scope["user"] = AnonymousUser()
                await self.close(code=4001) 
        else:
            self.scope["user"] = AnonymousUser()
            await self.close(code=4002)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def receive(self, text_data):
        await self.send(text_data=json.dumps({
            'status': 'got your message'
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def broadcast_message(self, event):
        message = event['data']
        sender_id = message.get('user_id')
        if self.scope['user'] and str(self.scope['user'].user_id) != str(sender_id):
            await self.send(text_data=json.dumps(message))

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(user_id=user_id)