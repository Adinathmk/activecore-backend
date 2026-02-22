from rest_framework import serializers
from apps.accounts.models import User


class AdminUserListSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "status",
        ]

    def get_status(self, obj):
        return "Active" if obj.is_active else "Blocked"