from rest_framework import serializers
from apps.products.models import (
    Product,
    Category,
    ProductType,
    ProductImage,
    ProductFeature,
    ProductVariant,
    Inventory,
    ProductMetrics,
    ProductRating,
)


# -----------------------------------
# Category Serializer
# -----------------------------------

class AdminCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")


# -----------------------------------
# Product Type Serializer
# -----------------------------------

class AdminProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ("id", "name", "slug", "is_active")


# -----------------------------------
# Inventory Serializer
# -----------------------------------

class AdminInventorySerializer(serializers.ModelSerializer):
    available_stock = serializers.IntegerField(read_only=True)

    class Meta:
        model = Inventory
        fields = ("stock", "reserved", "available_stock")


# -----------------------------------
# Variant Serializer
# -----------------------------------

class AdminVariantDetailSerializer(serializers.ModelSerializer):
    inventory = AdminInventorySerializer(read_only=True)
    selling_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "size",
            "sku",
            "price",
            "discount_percent",
            "selling_price",
            "is_active",
            "inventory",
        )


# -----------------------------------
# Image Serializer
# -----------------------------------

class AdminProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = (
            "id",
            "image_url",
            "is_primary",
            "is_secondary",
            "order",
        )


# -----------------------------------
# Feature Serializer
# -----------------------------------

class AdminProductFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFeature
        fields = ("id", "text")


# -----------------------------------
# Rating Serializer
# -----------------------------------

class AdminProductRatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = ProductRating
        fields = (
            "id",
            "user",
            "rating",
            "created_at",
        )


# -----------------------------------
# Metrics Serializer
# -----------------------------------

class AdminProductMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMetrics
        fields = ("avg_rating", "rating_count")


# -----------------------------------
# MAIN COMPLETE PRODUCT DETAIL
# -----------------------------------

class AdminProductDetailSerializer(serializers.ModelSerializer):

    category = AdminCategorySerializer(read_only=True)
    product_type = AdminProductTypeSerializer(read_only=True)

    images = AdminProductImageSerializer(many=True, read_only=True)
    features = AdminProductFeatureSerializer(many=True, read_only=True)
    variants = AdminVariantDetailSerializer(many=True, read_only=True)
    ratings = AdminProductRatingSerializer(many=True, read_only=True)
    metrics = AdminProductMetricsSerializer(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "category",
            "product_type",
            "is_active",
            "is_new_arrival",
            "is_top_selling",
            "created_at",
            "images",
            "features",
            "variants",
            "metrics",
            "ratings",
        )
