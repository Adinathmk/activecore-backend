from rest_framework import serializers
from apps.products.models import Product
from apps.products.api.serializers.CategorySerializer import CategorySerializer
from apps.products.api.serializers.ProductFeatureSerializer import ProductFeatureSerializer
from apps.products.api.serializers.ProductImageSerializer import ProductImageSerializer
from apps.products.api.serializers.ProductTypeSerializer import ProductTypeSerializer
from apps.products.api.serializers.ProductVariantSerializer import ProductVariantSerializer


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    product_type = ProductTypeSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    features = ProductFeatureSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    avg_rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "category",
            "product_type",
            "images",
            "features",
            "variants",
            "avg_rating",
            "rating_count",
            "is_new_arrival",
            "is_top_selling",
            "created_at",
        )



    def get_avg_rating(self, obj):
        if hasattr(obj, "metrics") and obj.metrics:
            return obj.metrics.avg_rating
        return 0

    def get_rating_count(self, obj):
        if hasattr(obj, "metrics") and obj.metrics:
            return obj.metrics.rating_count
        return 0
