from rest_framework import serializers
from django.db import transaction

from apps.products.models import (
    Product,
    ProductImage,
    ProductFeature,
    ProductVariant,
    Inventory,
)


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


class ImageUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    image = serializers.FileField(required=False, allow_null=True)
    image_url = serializers.URLField(required=False, allow_null=True)
    is_primary = serializers.BooleanField(default=False)
    is_secondary = serializers.BooleanField(default=False)


class ProductFullUpdateSerializer(serializers.ModelSerializer):

    images = ImageUpdateSerializer(many=True, required=False)
    features = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    variants = VariantUpdateSerializer(many=True, required=False)

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
            "is_featured",
            "images",
            "features",
            "variants",
        )

    # -------------------------
    # VALIDATIONS
    # -------------------------

    def validate_is_featured(self, value):
        if value:
            featured_count = Product.objects.filter(
                is_featured=True
            ).exclude(id=self.instance.id if self.instance else None).count()

            if featured_count >= 4:
                raise serializers.ValidationError(
                    "Maximum 4 featured products allowed."
                )
        return value

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

    # -------------------------
    # UPDATE PRODUCT
    # -------------------------

    @transaction.atomic
    def update(self, instance, validated_data):

        images_data = validated_data.pop("images", None)
        features_data = validated_data.pop("features", None)
        variants_data = validated_data.pop("variants", None)

        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # -------------------------
        # UPDATE IMAGES
        # -------------------------

        if images_data is not None:
            # We want to keep existing images if they have an ID and no new 'image' file
            # and delete those not sent + create new ones
            
            existing_image_ids = [img["id"] for img in images_data if img.get("id")]
            instance.images.exclude(id__in=existing_image_ids).delete()

            for index, img_data in enumerate(images_data):
                if img_data.get("id"):
                    # Update existing image layout
                    try:
                        img_obj = instance.images.get(id=img_data["id"])
                        img_obj.is_primary = img_data.get("is_primary", False)
                        img_obj.is_secondary = img_data.get("is_secondary", False)
                        img_obj.order = index
                        if img_data.get("image"):
                            img_obj.image = img_data["image"]
                        img_obj.save()
                    except ProductImage.DoesNotExist:
                        pass
                else:
                    # Create new image
                    if img_data.get("image"):
                        ProductImage.objects.create(
                            product=instance,
                            image=img_data["image"],
                            is_primary=img_data.get("is_primary", False),
                            is_secondary=img_data.get("is_secondary", False),
                            order=index
                        )

        # -------------------------
        # UPDATE FEATURES
        # -------------------------

        if features_data is not None:
            instance.features.all().delete()

            for feature in features_data:
                ProductFeature.objects.create(
                    product=instance,
                    text=feature
                )

        # -------------------------
        # UPDATE VARIANTS
        # -------------------------

        if variants_data is not None:

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

                    variant = existing_variants[size]
                    variant.price = variant_data["price"]
                    variant.discount_percent = variant_data.get(
                        "discount_percent", 0
                    )
                    variant.is_active = True
                    variant.save()

                    if hasattr(variant, "inventory"):
                        variant.inventory.stock = stock
                        variant.inventory.save()
                    else:
                        Inventory.objects.create(
                            variant=variant,
                            stock=stock
                        )

                else:

                    new_variant = ProductVariant.objects.create(
                        product=instance,
                        **variant_data
                    )

                    Inventory.objects.update_or_create(
                        variant=new_variant,
                        defaults={"stock": stock}
                    )

            # deactivate removed variants
            for size, variant in existing_variants.items():
                if size not in submitted_sizes:
                    variant.is_active = False
                    variant.save(update_fields=["is_active"])

        return instance