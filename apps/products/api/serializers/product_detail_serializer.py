from rest_framework import serializers
from apps.products.models import Product
from apps.products.api.serializers.category_serializer import CategorySerializer
from apps.products.api.serializers.product_feature_serializer import ProductFeatureSerializer
from apps.products.api.serializers.product_image_serializer import ProductImageSerializer
from apps.products.api.serializers.product_type_serializer import ProductTypeSerializer
from apps.products.api.serializers.product_variant_serializer import ProductVariantSerializer


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    product_type = ProductTypeSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    features = ProductFeatureSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    avg_rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()

    is_in_wishlist = serializers.SerializerMethodField()
    is_in_cart = serializers.SerializerMethodField()

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
            "is_in_wishlist",
            "is_in_cart",
        )



    def get_avg_rating(self, obj):
        if hasattr(obj, "metrics") and obj.metrics:
            return obj.metrics.avg_rating
        return 0

    def get_rating_count(self, obj):
        if hasattr(obj, "metrics") and obj.metrics:
            return obj.metrics.rating_count
        return 0
    def get_is_in_wishlist(self, obj):
        wishlist_variant_ids = self.context.get("wishlist_variant_ids", set())

        for variant in obj.variants.all():
            if variant.id in wishlist_variant_ids:
                return True
        return False


    def get_is_in_cart(self, obj):
        cart_variant_ids = self.context.get("cart_variant_ids", set())

        for variant in obj.variants.all():
            if variant.id in cart_variant_ids:
                return True
        return False