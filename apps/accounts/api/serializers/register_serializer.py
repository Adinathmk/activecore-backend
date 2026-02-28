# apps/accounts/serializers/register.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
import re

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"}
    )

    phone_number = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "first_name",
            "last_name",
            "phone_number",
        )

    # ================= EMAIL VALIDATION =================
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    # ================= PASSWORD VALIDATION =================
    def validate_password(self, value):
        validate_password(value)
        return value

    # ================= PHONE VALIDATION =================
    def validate_phone_number(self, value):
        """
        Validates phone number format.
        Example: +919876543210 or 9876543210
        """

        # Remove spaces and dashes
        value = value.replace(" ", "").replace("-", "")

        # Basic regex: optional +countrycode and 10-15 digits
        phone_regex = r"^\+?\d{10,15}$"

        if not re.match(phone_regex, value):
            raise serializers.ValidationError(
                "Enter a valid phone number (10–15 digits, optional +country code)"
            )

        # Optional: Check uniqueness
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already registered")

        return value

    # ================= CREATE USER =================
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            phone_number=validated_data["phone_number"],
            role=User.Role.CUSTOMER,
            is_verified=False,
            is_active=True,
        )
        return user