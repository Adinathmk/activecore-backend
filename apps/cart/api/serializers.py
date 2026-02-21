from rest_framework import serializers
from ..models import CartItem,Cart


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="variant.product.name", read_only=True)
    product_slug = serializers.CharField(source="variant.product.slug", read_only=True)
    size = serializers.CharField(source="variant.size", read_only=True)
    product_image = serializers.SerializerMethodField()
    available_stock = serializers.IntegerField(
        source="variant.inventory.available_stock",
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            "id",
            "variant",
            "product_name",
            "product_slug",
            "size",
            "product_image",
            "unit_price",
            "quantity",
            "total_price",
            "available_stock",

        ]

    def get_product_image(self, obj):
        image = obj.variant.product.images.filter(is_primary=True).first()
        return image.image_url if image else None
    


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "item_count",
            "subtotal",
            "tax_amount",
            "shipping_amount",
            "total_amount",
            "items",
        ]

    def get_item_count(self, obj):
        return sum(item.quantity for item in obj.items.all())
    


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0)

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value
    