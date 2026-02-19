from rest_framework import serializers
from django.db import transaction

from apps.products.models import (
    Product,
    ProductImage,
    ProductFeature,
    ProductVariant,
    Inventory,
)


# -----------------------------------
# Nested Variant Update Serializer
# -----------------------------------

class VariantUpdateSerializer(serializers.Serializer):
    size = serializers.ChoiceField(choices=ProductVariant.SIZE_CHOICES)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        default=0
    )
    stock = serializers.IntegerField(min_value=0)


# -----------------------------------
# Nested Image Update Serializer
# -----------------------------------

class ImageUpdateSerializer(serializers.Serializer):
    image_url = serializers.URLField()
    is_primary = serializers.BooleanField(default=False)
    is_secondary = serializers.BooleanField(default=False)


# -----------------------------------
# Main Full Update Serializer
# -----------------------------------

class ProductFullUpdateSerializer(serializers.ModelSerializer):

    images = ImageUpdateSerializer(many=True)
    features = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    variants = VariantUpdateSerializer(many=True)

    class Meta:
        model = Product
        fields = (
            "name",
            "description",
            "category",
            "product_type",
            "is_active",
            "is_new_arrival",
            "is_top_selling",
            "images",
            "features",
            "variants",
        )

    # -----------------------------------
    # Image Validation
    # -----------------------------------

    def validate_images(self, value):
        primary_count = sum(1 for img in value if img.get("is_primary"))
        secondary_count = sum(1 for img in value if img.get("is_secondary"))

        if primary_count != 1:
            raise serializers.ValidationError(
                "Exactly one primary image is required."
            )

        if secondary_count > 1:
            raise serializers.ValidationError(
                "Only one secondary image is allowed."
            )

        return value

    # -----------------------------------
    # Full Update Logic
    # -----------------------------------

    @transaction.atomic
    def update(self, instance, validated_data):
        images_data = validated_data.pop("images")
        features_data = validated_data.pop("features", [])
        variants_data = validated_data.pop("variants")

        # 1️⃣ Update Product Basic Fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # 2️⃣ Replace Images (Safe Replace Strategy)
        instance.images.all().delete()

        for index, image in enumerate(images_data):
            ProductImage.objects.create(
                product=instance,
                image_url=image["image_url"],
                is_primary=image.get("is_primary", False),
                is_secondary=image.get("is_secondary", False),
                order=index
            )

        # 3️⃣ Replace Features
        instance.features.all().delete()

        for feature in features_data:
            ProductFeature.objects.create(
                product=instance,
                text=feature
            )

        # 4️⃣ Update Variants (Smart Matching by Size)

        existing_variants = {
            variant.size: variant
            for variant in instance.variants.all()
        }

        submitted_sizes = []

        for variant_data in variants_data:
            size = variant_data["size"]
            stock = variant_data.pop("stock")
            submitted_sizes.append(size)

            if size in existing_variants:
                # Update existing variant
                variant = existing_variants[size]
                variant.price = variant_data["price"]
                variant.discount_percent = variant_data.get(
                    "discount_percent", 0
                )
                variant.is_active = True
                variant.save()

                # Update inventory
                if hasattr(variant, "inventory"):
                    variant.inventory.stock = stock
                    variant.inventory.save()
                else:
                    Inventory.objects.create(
                        variant=variant,
                        stock=stock
                    )
            else:
                # Create new variant
                new_variant = ProductVariant.objects.create(
                    product=instance,
                    **variant_data
                )
                Inventory.objects.update_or_create(
                    variant=new_variant,
                    stock=stock
                )

        # 5️⃣ Deactivate Removed Variants (Soft deactivate)
        for size, variant in existing_variants.items():
            if size not in submitted_sizes:
                variant.is_active = False
                variant.save(update_fields=["is_active"])

        return instance
