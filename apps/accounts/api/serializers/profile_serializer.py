# apps/accounts/api/serializers/profile_serializer.py

from rest_framework import serializers
from django.core.validators import RegexValidator
from ...models import User, Address
from .user_serializer import AddressSerializer


indian_phone_validator = RegexValidator(
    regex=r'^[6-9]\d{9}$',
    message="Enter a valid 10-digit Indian mobile number."
)


class UpdateProfileSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False)
    profile_image = serializers.ImageField(required=False)

    phone_number = serializers.CharField(
        required=False,
        allow_blank=True,
        validators=[indian_phone_validator]
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "profile_image",
            "address",
        ]

    # -----------------------------
    # FIELD VALIDATION
    # -----------------------------

    def validate_first_name(self, value):
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError(
                "First name must be at least 2 characters long."
            )
        return value.strip()

    def validate_last_name(self, value):
        if value and len(value.strip()) < 1:
            raise serializers.ValidationError(
                "Last name cannot be empty."
            )
        return value.strip()

    def validate_profile_image(self, value):
        if value.size > 2 * 1024 * 1024:  # 2MB limit
            raise serializers.ValidationError(
                "Image size must be under 2MB."
            )

        if not value.content_type.startswith("image/"):
            raise serializers.ValidationError(
                "Uploaded file must be an image."
            )

        return value

    # -----------------------------
    # UPDATE LOGIC
    # -----------------------------

    def update(self, instance, validated_data):
        address_data = validated_data.pop("address", None)

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Update or create address safely
        if address_data:
            address, created = Address.objects.get_or_create(user=instance)

            for attr, value in address_data.items():
                if value is not None:  # prevent accidental null overwrite
                    setattr(address, attr, value)

            address.save()

        return instance