from rest_framework import serializers
from ..models import WishlistItem

class WishlistItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
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

    def get_product(self, obj):
        from apps.products.api.serializers.product_list_serializer import ProductListSerializer
        return ProductListSerializer(
            obj.product_variant.product,   # ✅ FIXED
            context=self.context
        ).data

    def get_is_price_dropped(self, obj):
        return obj.product_variant.selling_price < obj.price_at_added