from rest_framework import serializers
from apps.products.models import Product

class FeaturedProductSerializer(serializers.ModelSerializer):
    primary_image = serializers.SerializerMethodField()
    secondary_image = serializers.SerializerMethodField()
    avg_rating = serializers.DecimalField(
        source="metrics.avg_rating",
        max_digits=2,
        decimal_places=1,
        read_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "slug",
            "primary_image",
            "secondary_image",
            "avg_rating",
        ]

    def get_primary_image(self, obj):
        image = next((img for img in obj.images.all() if img.is_primary), None)
        return image.image.url if image and image.image else None

    def get_secondary_image(self, obj):
        image = next((img for img in obj.images.all() if img.is_secondary), None)
        return image.image.url if image and image.image else None