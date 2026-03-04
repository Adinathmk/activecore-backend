from rest_framework import serializers
from apps.accounts.models import User


class AdminUserListSerializer(serializers.ModelSerializer):
    wishlist_count = serializers.SerializerMethodField()
    cart_count = serializers.SerializerMethodField()
    order_count = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",  
            "role",
            "is_verified",
            "status",
            "wishlist_count",
            "cart_count",
            "order_count",
        ]

    def get_wishlist_count(self, obj):
        if hasattr(obj, "wishlist"):
            return obj.wishlist.items.count()
        return 0

    def get_cart_count(self, obj):
        if hasattr(obj, "cart"):
            return obj.cart.items.count()
        return 0

    def get_order_count(self, obj):
        return obj.orders.count()

    def get_status(self, obj):
        return "Active" if obj.is_active else "Blocked"