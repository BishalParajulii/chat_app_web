import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatMessage , Message
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone
from .utils import format_timestamp
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.roomGroupName = "group_chat_gfg"
        await self.channel_layer.group_add(
            self.roomGroupName,
            self.channel_name
        )
        await self.accept()

        messages = await self.get_last_message()
        for msg in messages:
            await self.send(text_data=json.dumps({
                'message': msg['message'],
                'username': msg['username'],
                'timestamp': msg['timestamp'],
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.roomGroupName,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        username = data["username"]

        await self.save_message(username, message)

        await self.channel_layer.group_send(
            self.roomGroupName, {
                "type": "sendMessage",
                "message": message,
                "username": username,
                "timestamp": timezone.now().isoformat()
            }
        )

    async def sendMessage(self, event):
        message = event["message"]
        username = event["username"]
        timestamp = event["timestamp"]
        await self.send(text_data=json.dumps({
            "message": message,
            "username": username,
            "timestamp": timestamp
        }))

    @sync_to_async
    def save_message(self, username, message):
        try:
            user = User.objects.get(username=username)
            ChatMessage.objects.create(user=user, message=message)
        except User.DoesNotExist:
            pass


    @sync_to_async
    def get_last_message(self):
        user = self.scope["user"]
        if user.is_authenticated:
            joined_at = user.date_joined
            messages = ChatMessage.objects.select_related('user').filter(timestamp__gte=joined_at).order_by('timestamp')
            return [
                {
                    "username": msg.user.username,
                    "message": msg.message,
                    "timestamp": msg.timestamp.isoformat()  # ✅ FIXED HERE
                }
                for msg in messages
            ]
        return []






from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import User, Message
from django.utils import timezone
import json

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.sender = self.scope['user']
        self.receiver_id = self.scope['url_route']['kwargs']['user_id']
        self.receiver = await sync_to_async(User.objects.get)(id=self.receiver_id)

        self.room_name = f"chat_{min(self.sender.id , self.receiver.id)}_{max(self.sender.id , self.receiver.id)}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()

        # Send last messages to the WebSocket client
        messages = await self.get_last_messages()
        for msg in messages:
            await self.send(text_data=json.dumps(msg))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        # Save the message to the database
        await self.save_message(self.sender, self.receiver, message)

        # Send the message to the group
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "send_message",
                "message": message,
                "sender": self.sender.username,
                "sender_id": self.sender.id,  # Send sender's id to frontend
                "timestamp": timezone.now().isoformat()
            }
        )

    async def send_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "sender_id": event["sender_id"],  # Include sender's id in the message
            "timestamp": event["timestamp"]
        }))

    @sync_to_async
    def get_last_messages(self):
        # Retrieve the last 50 messages between the sender and receiver
        messages = Message.objects.filter(
            sender__in=[self.sender, self.receiver],
            receiver__in=[self.sender, self.receiver]
        ).order_by('timestamp')[:50]

        return [
            {
                "sender": msg.sender.username,
                "message": msg.message,
                "timestamp": msg.timestamp.isoformat(),
                "sender_id": msg.sender.id  # Include sender's id in each message
            }
            for msg in messages
        ]
    
    @sync_to_async
    def save_message(self, sender, receiver, message):
        # Save the new message to the database
        Message.objects.create(
            sender=sender,
            receiver=receiver,
            message=message
        )
