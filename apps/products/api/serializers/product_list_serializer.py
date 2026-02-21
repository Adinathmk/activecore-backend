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
            "is_new_arrival",
            "is_top_selling",
            "in_stock",
            "is_in_wishlist",
            "is_in_cart"
        )

    # --------------------------------
    # Images
    # --------------------------------

    def get_primary_image(self, obj):
        image = next(
            (img for img in obj.images.all() if img.is_primary),
            None
        )
        return image.image_url if image else None

    def get_secondary_image(self, obj):
        secondary = [
            img for img in obj.images.all() if not img.is_primary
        ]
        return secondary[0].image_url if secondary else None

    # --------------------------------
    # Price (ONE variant – lowest)
    # --------------------------------

    def get_price(self, obj):
        prices = [
            variant.selling_price
            for variant in obj.variants.all()
            if variant.is_active
        ]
        return min(prices) if prices else None

    # --------------------------------
    # Stock
    # --------------------------------

    def get_in_stock(self, obj):
        return any(
            hasattr(v, "inventory") and v.inventory.available_stock > 0
            for v in obj.variants.all()
            if v.is_active
        )
    
    def get_is_in_wishlist(self, obj):  
        wishlist_variant_ids = self.context.get("wishlist_variant_ids", set())

        return any(
            variant.id in wishlist_variant_ids
            for variant in obj.variants.all()
            if variant.is_active
        )
    def get_is_in_cart(self, obj):
        cart_variant_ids = self.context.get("cart_variant_ids", set())

        for variant in obj.variants.all():
            if variant.id in cart_variant_ids:
                return True
        return False