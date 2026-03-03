from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password


# ===============================
# 🔹 Email Verification
# ===============================

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


# ===============================
# 🔹 Forgot Password
# ===============================

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    channel = serializers.ChoiceField(
        choices=["email", "whatsapp"],
        default="email"
    )


# ===============================
# 🔹 Reset Password
# ===============================

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    channel = serializers.ChoiceField(
        choices=["email", "whatsapp"]
    )
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"}
    )

    def validate_new_password(self, value):
        validate_password(value)
        return value