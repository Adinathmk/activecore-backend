from rest_framework import serializers
from django.db import transaction
from django.db.models import Avg, Count
from apps.products.models import ProductRating, ProductMetrics


class ProductRatingCreateSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = ProductRating
        fields = ("rating",)

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        product = self.context["product"]

        ProductRating.objects.update_or_create(
            product=product,
            user=user,
            defaults={"rating": validated_data["rating"]}
        )

        metrics, _ = ProductMetrics.objects.get_or_create(product=product)

        data = product.ratings.aggregate(
            avg=Avg("rating"),
            count=Count("id")
        )

        metrics.avg_rating = round(data["avg"] or 0, 1)
        metrics.rating_count = data["count"]
        metrics.save(update_fields=["avg_rating", "rating_count"])

        return product
