from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from .managers import UserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        ADMIN = "admin", "Admin"

    username = None

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    email = models.EmailField(
        unique=True, 
        db_index=True
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
        db_index=True
    )

    is_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = "email"
    
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

