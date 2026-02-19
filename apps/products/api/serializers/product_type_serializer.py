from rest_framework import serializers
from apps.products.models import ProductType


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ("name", "slug", "is_active")
    
    def validate_name(self, value):
        if ProductType.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError(
                "Product type already exists."
            )
        return value
