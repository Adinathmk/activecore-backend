from rest_framework import serializers
from apps.products.models import Product


class AdminProductListSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    product_type = serializers.StringRelatedField()
    avg_rating = serializers.DecimalField(
        source="metrics.avg_rating",
        max_digits=2,
        decimal_places=1,
        read_only=True
    )
    rating_count = serializers.IntegerField(
        source="metrics.rating_count",
        read_only=True
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "category",
            "product_type",
            "is_active",
            "is_new_arrival",
            "is_top_selling",
            "created_at",
            "avg_rating",
            "rating_count",
        )
