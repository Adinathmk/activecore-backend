import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .services import get_ai_response
from .models import ChatMessage


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        user = self.scope.get("user")

        if user and user.is_authenticated:
            await self.accept()
        else:
            await self.close()

    async def receive(self, text_data):

        data = json.loads(text_data)
        user_message = data.get("message")

        user = self.scope["user"]

        # Save user message
        await database_sync_to_async(ChatMessage.objects.create)(
            user=user,
            role="user",
            message=user_message
        )

        # Call AI safely (run blocking code in thread)
        ai_reply = await database_sync_to_async(get_ai_response)(user_message)

        # Save AI message
        await database_sync_to_async(ChatMessage.objects.create)(
            user=user,
            role="assistant",
            message=ai_reply
        )

        # Send reply to frontend
        await self.send(
            text_data=json.dumps({
                "response": ai_reply
            })
        )