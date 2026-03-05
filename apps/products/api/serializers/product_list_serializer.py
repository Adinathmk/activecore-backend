from rest_framework import serializers
from apps.products.models import Product


class ProductListSerializer(serializers.ModelSerializer):
    product_type = serializers.CharField(
        source="product_type.name",
        read_only=True
    )

    primary_image = serializers.SerializerMethodField()
    secondary_image = serializers.SerializerMethodField()

    price = serializers.SerializerMethodField()
    variant_id = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    is_in_wishlist = serializers.SerializerMethodField()
    is_in_cart = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "product_type",
            "primary_image",
            "secondary_image",
            "price",
            "variant_id",
            "is_new_arrival",
            "is_top_selling",
            "in_stock",
            "is_in_wishlist",
            "is_in_cart",
        )

    # -------------------------
    # Helper Method
    # -------------------------
    def _get_default_variant(self, obj):
        active_variants = [
            v for v in obj.variants.all()
            if v.is_active
        ]

        if not active_variants:
            return None

        # Variants with stock
        in_stock_variants = [
            v for v in active_variants
            if hasattr(v, "inventory") and v.inventory.available_stock > 0
        ]

        # Prefer in-stock variants
        variants_to_consider = in_stock_variants if in_stock_variants else active_variants

        return min(variants_to_consider, key=lambda v: v.selling_price)

    # -------------------------
    # Images
    # -------------------------
    def get_primary_image(self, obj):
        image = next(
            (img for img in obj.images.all() if img.is_primary),
            None
        )
        return image.image.url if image and image.image else None

    def get_secondary_image(self, obj):
        image = next(
            (img for img in obj.images.all() if img.is_secondary),
            None
        )
        return image.image.url if image and image.image else None

    # -------------------------
    # Price
    # -------------------------
    def get_price(self, obj):
        variant = self._get_default_variant(obj)
        return variant.selling_price if variant else None

    # -------------------------
    # Variant ID (Default Variant)
    # -------------------------
    def get_variant_id(self, obj):
        variant = self._get_default_variant(obj)
        return variant.id if variant else None

    # -------------------------
    # Stock
    # -------------------------
    def get_in_stock(self, obj):
        variant = self._get_default_variant(obj)
        return (
            hasattr(variant, "inventory") and
            variant.inventory.available_stock > 0
        ) if variant else False

    # -------------------------
    # Wishlist
    # -------------------------
    def get_is_in_wishlist(self, obj):
        wishlist_variant_ids = self.context.get("wishlist_variant_ids", set())
        active_variants = [
            v for v in obj.variants.all()
            if v.is_active
        ]

        return any(
            v.id in wishlist_variant_ids
            for v in active_variants
        )

    # -------------------------
    # Cart
    # -------------------------
    def get_is_in_cart(self, obj):
        cart_variant_ids = self.context.get("cart_variant_ids", set())
        active_variants = [
            v for v in obj.variants.all()
            if v.is_active
        ]

        return any(
            v.id in cart_variant_ids
            for v in active_variants
        )