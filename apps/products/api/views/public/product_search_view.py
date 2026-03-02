from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from django.db.models import Q
from django.db.models import Prefetch

from drf_spectacular.utils import extend_schema

from apps.products.models import Product, ProductVariant, ProductImage
from apps.products.api.serializers.product_list_serializer import ProductListSerializer


class ProductSearchAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["products"],
        summary="Global product search",
    )
    def get(self, request):

        query = request.query_params.get("q", "").strip()
        limit = int(request.query_params.get("limit", 10))

        if not query:
            return Response([], status=status.HTTP_200_OK)

        # Safety limit (prevent abuse)
        limit = min(limit, 20)

        queryset = (
            Product.objects
            .filter(is_active=True)
            .select_related("category", "product_type")
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=ProductImage.objects.order_by("order"),
                ),
                Prefetch(
                    "variants",
                    queryset=ProductVariant.objects.filter(is_active=True)
                )
            )
            .filter(
                Q(name__istartswith=query) |
                Q(category__name__istartswith=query) |
                Q(product_type__name__istartswith=query) |
                Q(description__icontains=query)
            )
            .distinct()
            .order_by("name")[:limit]
        )

        serializer = ProductListSerializer(
            queryset,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)