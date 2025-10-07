import json
import base64
from django.core.files.base import ContentFile
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import *
import asyncio



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        self.room_name = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f"chat_{self.room_name}"
        if await self.check_able_connect_or_not():
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get("message", "")
        files_data = data.get("files", [])  # [{"title":"img.png","file_base64":"data:image/png;base64,...."}]
        # Save message + files
        message_obj = await self.save_message_to_database(message_text, files_data)
        files_urls = await self.get_message_files(message_obj)
        # Broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message_text,
                "username": getattr(self.user, "username", "Anonymous"),
                "profile_image": self.user.image.url if self.user and self.user.image else None,
                "last_activity": str(self.user.last_activity) if self.user.last_activity else None,
                "files": files_urls
            }
        )
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "username": event["username"],
            "image": event["profile_image"],
            "last_activity":event['last_activity'],
            "files": event.get("files", [])
        }))

    # ---------------- DB helpers ----------------

    @database_sync_to_async
    def check_able_connect_or_not(self):
        chat = Chat.objects.get(id=self.room_name)
        return self.user in chat.participants.all()

    @database_sync_to_async
    def get_message_files(self, message_obj):
        return [f.file.url for f in message_obj.files.all()]

    @database_sync_to_async
    def save_message_to_database(self, message_text, files):
        chat = Chat.objects.get(id=self.room_name)
        msg_obj = Message.objects.create(chat=chat, sender=self.user, text=message_text)

        for f in files:
            title = f.get("title", "")
            file_base64 = f.get("file_base64")
            if file_base64:
                format, imgstr = file_base64.split(';base64,')
                ext = format.split('/')[-1]  # e.g., png, jpg
                data = ContentFile(base64.b64decode(imgstr), name=f"{title}.{ext}")
                file_obj = MessageFiles.objects.create(title=title, file=data)
                msg_obj.files.add(file_obj)
        chat.save()

        return msg_obj


class MessageSeenStatusUpdate(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        self.room_name = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f"message_update_seen_{self.room_name}"

        if await self.check_able_connect_or_not():
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

            # Start the broadcast loop as a background task
            self.loop_task = asyncio.create_task(self.broadcast_loop())
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Stop the background loop
        if hasattr(self, "loop_task"):
            self.loop_task.cancel()
            try:
                await self.loop_task
            except asyncio.CancelledError:
                pass

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # Handle messages from client (optional)
        if text_data:
            data = json.loads(text_data)
            print("Received from client:", data)

    async def broadcast_loop(self):

        try:
            while True:
                await self.chat_object_message_object_update()
                message_text = "successfully done"
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "update_message",
                        "message": message_text
                    }
                )
                await asyncio.sleep(1)  # wait 5 seconds before sending next
        except asyncio.CancelledError:
            # Loop stops when disconnect is called
            print(f"Broadcast loop stopped for user {self.user.username}")

    async def update_message(self, event):
        # await self.chat_object_message_object_update()
        # Send the message to WebSocket client
        await self.send(text_data=json.dumps({
            "message": event["message"]
        }))

    @database_sync_to_async
    def check_able_connect_or_not(self):
        chat = Chat.objects.get(id=self.room_name)
        return self.user in chat.participants.all()

    @database_sync_to_async
    def chat_object_message_object_update(self):
        chat = Chat.objects.get(id=self.room_name)
        mgs = Message.objects.filter(chat=chat, seen_users = self.user).first()
        if mgs:
            mgs.seen_users.remove(self.user)
            mgs.save()
        letest_message = Message.objects.filter(chat=chat).order_by("-created_at").first()
        letest_message.seen_users.add(self.user)
        letest_message.save()

        return self.user 


class Sent_Reaction_ON_Message(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        self.room_name = self.scope['url_route']['kwargs']['message_id']
        self.room_group_name = f"react_to_{self.room_name}"

        if await self.check_able_connect_or_not():
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        emuji = data.get("message", "")

        await self.save_reaction_into_message(emuji)


        # Broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "emoji_sender",
                "message": emuji,
                "username": getattr(self.user, "username", None),
                "profile_image": getattr(self.user, "profile_image", None).url if getattr(self.user, "profile_image", None) else None,
                "last_activity": getattr(self.user, "last_activity", None),
             
            }
        )

    async def emoji_sender(self, event):
        await self.send(text_data=json.dumps({
            "emuji": event["message"],
            "username": event["username"],
            "profile_image": event["profile_image"], 
            "last_activity": event["last_activity"],
            "message_id":self.room_name
            
        }))

    # ---------------- DB helpers ----------------

    @database_sync_to_async
    def check_able_connect_or_not(self):
        message = Message.objects.get(id=self.room_name)
        return self.user in message.chat.participants.all()

    @database_sync_to_async
    def save_reaction_into_message(self, emuji):
        try:
            message = Message.objects.get(id = self.room_name)
            if MessageReaction.objects.filter(user = self.user, emoji = emuji).exists():
                reaction = MessageReaction.objects.filter(user = self.user, emoji = emuji).first()
            else:
                reaction = MessageReaction.objects.create(
                    user=self.user,
                    emoji = emuji
                )
            message.reactions.add(reaction)
            message.save()
            return emuji
        except:
            return "message not found"
































from channels.generic.websocket import AsyncJsonWebsocketConsumer

class CallConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"call_{self.room_name}"
        # join group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # leave group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        # notify others (optional)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "signal.message",
                "action": "leave",
                "data": {"channel": self.channel_name},
                "sender_channel": self.channel_name,
            },
        )

    async def receive_json(self, content, **kwargs):
        """
        Expected message shape from client:
        { action: "offer"|"answer"|"ice"|"join"|..., data: { ... } }
        """
        action = content.get("action")
        data = content.get("data", {})

        # Basic validation
        if action not in ("offer", "answer", "ice", "join", "leave", "hangup", "toggle_mute"):
            return  # ignore unknown

        # broadcast to room (you can extend to target a specific peer)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "signal.message",
                "action": action,
                "data": data,
                "sender_channel": self.channel_name,
                # optional: include user info:
                "sender_user": getattr(self.scope.get("user"), "username", None),
            },
        )

    async def signal_message(self, event):
        """
        Handler for group messages -> forward to ws clients.
        Avoid sending the original message back to the sender.
        """
        # don't echo to the sender
        if event.get("sender_channel") == self.channel_name:
            return

        await self.send_json(
            {
                "action": event["action"],
                "data": event.get("data", {}),
                "sender_user": event.get("sender_user"),
            }
        )
