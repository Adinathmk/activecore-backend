from rest_framework import serializers
from ..models import WishlistItem
from apps.products.api.serializers.product_list_serializer import ProductListSerializer

class WishlistItemSerializer(serializers.ModelSerializer):

    variant_id = serializers.IntegerField(
        source="product_variant.id",
        read_only=True
    )

    size = serializers.CharField(
        source="product_variant.size",
        read_only=True
    )

    selling_price = serializers.DecimalField(
        source="product_variant.selling_price",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    product = ProductListSerializer(
        source="product_variant.product",
        read_only=True
    )

    is_price_dropped = serializers.SerializerMethodField()

    class Meta:
        model = WishlistItem
        fields = [
            "id",
            "size",
            "variant_id",
            "product",
            "price_at_added",
            "selling_price",
            "is_price_dropped",
            "added_at",
        ]

    def get_is_price_dropped(self, obj):
        variant = obj.product_variant
        if not variant:
            return False
        return variant.selling_price < obj.price_at_added