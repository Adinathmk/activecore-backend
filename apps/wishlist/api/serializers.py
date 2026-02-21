from rest_framework import serializers
from ..models import WishlistItem
from apps.products.api.serializers.product_list_serializer import ProductListSerializer

class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(
        source="product_variant.product",
        read_only=True
    )
    is_price_dropped = serializers.SerializerMethodField()

    class Meta:
        model = WishlistItem
        fields = [
            "id",
            "product",
            "price_at_added",
            "is_price_dropped",
            "added_at",
        ]

    def get_is_price_dropped(self, obj):
        return obj.product_variant.selling_price < obj.price_at_added