from rest_framework import serializers
from apps.products.models import ProductRating

class ProductRatingCreateSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)

