from rest_framework import serializers
from django.db import transaction

from apps.products.models import ProductVariant, Inventory, Product


class AdminVariantListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    stock = serializers.IntegerField(source="inventory.stock", read_only=True)
    available_stock = serializers.IntegerField(source="inventory.available_stock", read_only=True)

    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "product_id",
            "product_name",
            "size",
            "sku",
            "price",
            "discount_percent",
            "selling_price",
            "is_active",
            "stock",
            "available_stock",
        )


class AdminVariantCreateUpdateSerializer(serializers.ModelSerializer):
    stock = serializers.IntegerField(write_only=True, min_value=0, default=0)
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), required=True
    )

    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "product",
            "size",
            "price",
            "discount_percent",
            "is_active",
            "stock",
        )

    def validate(self, attrs):
        product = attrs.get("product")
        size = attrs.get("size")

        if self.instance:
            product = product or self.instance.product
            size = size or self.instance.size

        if ProductVariant.objects.filter(product=product, size=size).exclude(
            pk=self.instance.pk if self.instance else None
        ).exists():
            raise serializers.ValidationError(
                {"size": f"Variant with size '{size}' already exists for this product."}
            )

        return attrs

    def create(self, validated_data):
        stock = validated_data.pop("stock", 0)

        with transaction.atomic():
            variant = ProductVariant.objects.create(**validated_data)

            Inventory.objects.update_or_create(
                variant=variant,
                defaults={"stock": stock},
            )

        return variant

    def update(self, instance, validated_data):
        stock = validated_data.pop("stock", None)

        with transaction.atomic():
            # Update variant fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # Update inventory
            if stock is not None:
                inventory = instance.inventory

                if inventory.reserved > stock:
                    raise serializers.ValidationError(
                        {
                            "stock": f"Stock cannot be less than reserved quantity ({inventory.reserved})."
                        }
                    )

                inventory.stock = stock
                inventory.save()

        return instance