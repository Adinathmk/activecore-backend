from rest_framework import serializers
from ..models import Order, OrderItem
from apps.orders.models import OrderStatus


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"


class CheckoutSerializer(serializers.Serializer):
    shipping_address = serializers.JSONField()
    billing_address = serializers.JSONField()

    variant_id = serializers.IntegerField(required=False)
    quantity = serializers.IntegerField(required=False, min_value=1)
    payment_method = serializers.ChoiceField(
    choices=["ONLINE", "COD"],
    required=True
    )

    def validate(self, data):
        if data.get("variant_id") and not data.get("quantity"):
            raise serializers.ValidationError(
                "Quantity is required when buying single product."
            )
        return data



class AdminOrderStatusUpdateSerializer(serializers.Serializer):
    new_status = serializers.ChoiceField(choices=OrderStatus.choices)


class AccountOverviewSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    confirmed_orders= serializers.IntegerField()
    delivered_orders = serializers.IntegerField()
    cancelled_orders = serializers.IntegerField()
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2)

