from rest_framework import serializers
from apps.products.models import ProductVariant



class ProductVariantSerializer(serializers.ModelSerializer):
    selling_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    available_stock = serializers.IntegerField(
        source="inventory.available_stock",
        read_only=True
    )

    class Meta:
        model = ProductVariant
        fields = (
            "size",
            "price",
            "discount_percent",
            "selling_price",
            "available_stock",
            "is_active",
        )
