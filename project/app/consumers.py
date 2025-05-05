import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatMessage
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone
from .utils import format_timestamp

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




class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.sender = self.scope['user']
        self.receiver_username = self.scope['url_route']['kwargs']['username']
        self.receiver = await sync_to_async(User.objects.get)(username=self.receiver_username)

        self.room_name = f"chat_{min(self.sender.id , self.receiver.id)}_{max(self.sender.id , self.receiver.id)}"

        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()

        message = await self.get_last_message()
        for msg in message:
            await self.send(text_data=json.dumps(msg))

    async def  disconnect(self , close_code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self , text_data):
        data = json.loads(text_data)
        message = data['message']


        await self.save_message(self.sender, self.receiver, message)

        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "send_message",
                "message": message,
                "sender": self.sender.username,
                "timestamp": timezone.now().isoformat()
            }
        )

    async def send_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "timestamp": event["timestamp"]
        }))

    @sync_to_async
    def get_last_messages(self):
        messages = Message.objects.filter(
            sender__in=[self.sender, self.receiver],
            receiver__in=[self.sender, self.receiver]
        ).order_by('timestamp')

        return [
            {
                "sender": msg.sender.username,
                "message": msg.message,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]        
