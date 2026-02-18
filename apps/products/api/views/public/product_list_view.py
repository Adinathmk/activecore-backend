from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from django.db.models import Prefetch

from apps.products.models import Product, ProductVariant, ProductImage
from apps.products.api.serializers.product_list_serializer import (
    ProductListSerializer
)


class ProductListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = (
            Product.objects
            .filter(is_active=True)
            .select_related("product_type")
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=ProductImage.objects.order_by("order"),
                ),
                Prefetch(
                    "variants",
                    queryset=ProductVariant.objects
                    .filter(is_active=True)
                    .select_related("inventory"),
                ),
            )
        )

        params = request.query_params

        # -------------------------
        # Filters
        # -------------------------

        if params.get("new") == "true":
            queryset = queryset.filter(is_new_arrival=True)

        if params.get("top") == "true":
            queryset = queryset.filter(is_top_selling=True)

        if product_type := params.get("type"):
            queryset = queryset.filter(product_type__slug=product_type)

        if params.get("in_stock") == "true":
            queryset = queryset.filter(
                variants__inventory__stock__gt=0
            ).distinct()

        serializer = ProductListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )

        return Response(serializer.data, status=status.HTTP_200_OK)
