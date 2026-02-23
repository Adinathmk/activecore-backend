from rest_framework import serializers
from django.db import transaction

from apps.products.models import (
    Product,
    ProductImage,
    ProductFeature,
    ProductVariant,
    Inventory,
    ProductMetrics,
)


class VariantCreateSerializer(serializers.Serializer):
    size = serializers.ChoiceField(choices=ProductVariant.SIZE_CHOICES)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        default=0
    )
    stock = serializers.IntegerField(min_value=0)


class ImageCreateSerializer(serializers.Serializer):
    image_url = serializers.URLField()
    is_primary = serializers.BooleanField(default=False)
    is_secondary = serializers.BooleanField(default=False)


class ProductCreateSerializer(serializers.ModelSerializer):
    images = ImageCreateSerializer(many=True)
    features = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    variants = VariantCreateSerializer(many=True)

    class Meta:
        model = Product
        fields = (
            "name",
            "description",
            "category",
            "product_type",
            "is_new_arrival",
            "is_top_selling",
            "is_featured",
            "images",
            "features",
            "variants",
        )

    def validate_is_featured(self, value):
        if value:
            featured_count = Product.objects.filter(
                is_featured=True
            ).exclude(id=self.instance.id if self.instance else None).count()

            if featured_count >= 8:
                raise serializers.ValidationError(
                    "Maximum 8 featured products allowed."
                )
        return value
  

    def validate_images(self, value):
        primary_count = sum(1 for img in value if img.get("is_primary"))
        if primary_count != 1:
            raise serializers.ValidationError(
                "Exactly one primary image is required."
            )
        return value



    def validate_variants(self, value):
        sizes = [v["size"] for v in value]
        if len(sizes) != len(set(sizes)):
            raise serializers.ValidationError(
                "Duplicate variant sizes are not allowed."
            )
        return value

 
    @transaction.atomic
    def create(self, validated_data):
        images_data = validated_data.pop("images")
        features_data = validated_data.pop("features", [])
        variants_data = validated_data.pop("variants")


        product = Product.objects.create(**validated_data)

        ProductMetrics.objects.create(product=product)


        for index, image in enumerate(images_data):
            ProductImage.objects.create(
                product=product,
                image_url=image["image_url"],
                is_primary=image.get("is_primary", False),
                is_secondary=image.get("is_secondary", False),
                order=index
            )


        for feature in features_data:
            ProductFeature.objects.create(
                product=product,
                text=feature
            )

        for variant_data in variants_data:
            stock = variant_data.pop("stock")

            variant = ProductVariant.objects.create(
                product=product,
                **variant_data
            )


            Inventory.objects.update_or_create(
                variant=variant,
                defaults={"stock": stock}
            )

        return product
