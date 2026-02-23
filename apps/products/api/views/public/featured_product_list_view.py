
from django.db.models import Prefetch, Q
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.products.models import Product, ProductImage
from apps.products.api.serializers.featured_product_serializer import (
    FeaturedProductSerializer,
)


class FeaturedProductListView(ListAPIView):
    serializer_class = FeaturedProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return (
            Product.objects
            .filter(is_featured=True, is_active=True)
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=ProductImage.objects.filter(
                        Q(is_primary=True) | Q(is_secondary=True)
                    ),
                )
            )
            .select_related("metrics")
            .order_by("-created_at")[:4]   
        )