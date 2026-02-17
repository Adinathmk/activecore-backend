from rest_framework import serializers
from apps.products.models import ProductFeature

class ProductFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFeature
        fields = ("text",)