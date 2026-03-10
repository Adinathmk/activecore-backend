import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        user = self.scope.get("user")

       
        if user and user.is_authenticated:
            self.group_name = f"user_{user.id}"
            print(f"WebSocket Consumer: Joining group '{self.group_name}' for user {user.email}")
            
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            await self.accept()

            print(f"WebSocket connected for user {user.email} on channel {self.channel_name}")

        else:
           
            user_info = f"User: {user}" if user else "No user in scope"
            print(f"WebSocket rejected: {user_info}")
            await self.close()

    async def disconnect(self, close_code):

        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

        print("WebSocket disconnected")

    async def send_notification(self, event):
        print(f"WebSocket Consumer: Received message from group layer: {event['message']}")
        await self.send(
            text_data=json.dumps({
                "message": event["message"]
            })
        )