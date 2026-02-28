# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from .managers import UserManager
from cloudinary.models import CloudinaryField
from django.core.validators import RegexValidator

indian_phone_validator = RegexValidator(
    regex=r'^[6-9]\d{9}$',
    message="Enter a valid 10-digit Indian mobile number."
)


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

    # Optional fields
    phone_number = models.CharField(
        max_length=10,
        validators=[indian_phone_validator],
        blank=True,
        null=True
    )

    profile_image = CloudinaryField(
        "profile_image",
        folder="user_profiles",
        blank=True,
        null=True
    )

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

# -----------------------------------------------------------------------------------------------------------------------


class Address(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.OneToOneField(   # 🔥 Change this
        User,
        on_delete=models.CASCADE,
        related_name="address"
    )


    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)

    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["city"]),
        ]

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(
                user=self.user,
                is_default=True
            ).update(is_default=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} - {self.city}"


# ------------------------------------------------------------------------------------------------


import uuid
from datetime import timedelta
from django.utils import timezone
from django.conf import settings

class EmailOTP(models.Model):

    OTP_TYPES = (
        ("verify", "Verify Account"),
        ("reset", "Password Reset"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_hash = models.CharField(max_length=128)
    otp_type = models.CharField(max_length=10, choices=OTP_TYPES)
    attempts = models.IntegerField(default=0)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)