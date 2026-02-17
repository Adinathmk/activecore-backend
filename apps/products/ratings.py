# apps/products/ratings.py

from django.db import transaction
from django.db.models import Avg, Count

from .models import ProductRating, ProductMetrics


@transaction.atomic
def submit_rating(*, product, user, value):
    """
    Create or update a user's rating for a product
    and recalculate product metrics atomically.
    """

    ProductRating.objects.update_or_create(
        product=product,
        user=user,
        defaults={"rating": value}
    )

    metrics, _ = ProductMetrics.objects.get_or_create(product=product)

    data = product.ratings.aggregate(
        avg=Avg("rating"),
        count=Count("id")
    )

    metrics.avg_rating = round(data["avg"] or 0, 1)
    metrics.rating_count = data["count"]
    metrics.save(update_fields=["avg_rating", "rating_count"])
