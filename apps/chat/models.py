from django.db import models
from apps.accounts.models import User


class ChatMessage(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    role = models.CharField(
        max_length=10,
        choices=[
            ("user", "User"),
            ("assistant", "Assistant"),
        ]
    )

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)