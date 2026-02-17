from rest_framework import serializers
from apps.products.models import ProductImage



class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = (
            "image_url",
            "is_primary",
            "is_secondary",
            "order",
        )
