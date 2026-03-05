from rest_framework import serializers
from apps.products.models import ProductImage



class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = (
            "id",
            "image_url",
            "is_primary",
            "is_secondary",
            "order",
        )

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None
