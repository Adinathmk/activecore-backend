from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

from .models import Notification

User = get_user_model()
channel_layer = get_channel_layer()


def notify_user(user, message):

    Notification.objects.create(
        user=user,
        message=message
    )

    group_name = f"user_{user.id}"
    print(f"Notification Service: Sending message to group '{group_name}': {message}")

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_notification",
            "message": message
        }
    )
    logger.info(f"Real-time notification sent to User {user.id}")


def notify_all_users(message):

    users = User.objects.all()

    for user in users:

        Notification.objects.create(
            user=user,
            message=message
        )

        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",
            {
                "type": "send_notification",
                "message": message
            }
        )