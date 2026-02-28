from rest_framework import serializers
from ...models import Address,User
from django.core.validators import RegexValidator


indian_phone_validator = RegexValidator(
    regex=r'^[6-9]\d{9}$',
    message="Enter a valid 10-digit Indian mobile number."
)



class AddressSerializer(serializers.ModelSerializer):

    phone_number = serializers.CharField(
        validators=[indian_phone_validator],
        required=False
    )

    class Meta:
        model = Address
        exclude = ["user", "id", "created_at"]

    def validate_postal_code(self, value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError(
                "Postal code must be a valid 6-digit number."
            )
        return value

    def validate(self, data):
        required_fields = [
            "full_name",
            "address_line_1",
            "city",
            "state",
            "postal_code",
            "country"
        ]

        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(
                    {field: f"{field.replace('_', ' ').title()} is required."}
                )

        return data
    



class UserSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone_number",
            "profile_image",
            "role",
            "is_verified",
            "created_at",
            "address",
        ]
        read_only_fields = fields

    def get_profile_image(self, obj):
        if obj.profile_image:
            return obj.profile_image.url
        return None