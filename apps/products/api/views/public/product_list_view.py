from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from django.db.models import Prefetch, Min

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from apps.products.models import Product, ProductVariant, ProductImage
from apps.products.api.serializers.product_list_serializer import (
    ProductListSerializer
)


class ProductListAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["products"],
        summary="List products with filters and sorting",
        description=(
            "Returns a filtered and sorted list of active products.\n\n"
            "Supports:\n"
            "- Category filtering\n"
            "- Size filtering\n"
            "- Price range filtering\n"
            "- Sorting (newest, price ascending, price descending)"
        ),
        parameters=[
            OpenApiParameter(
                name="category",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by category slug",
            ),
            OpenApiParameter(
                name="size",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by size (XS, S, M, L, XL, XXL)",
            ),
            OpenApiParameter(
                name="min_price",
                type=OpenApiTypes.FLOAT,
                location=OpenApiParameter.QUERY,
                description="Minimum variant price",
            ),
            OpenApiParameter(
                name="max_price",
                type=OpenApiTypes.FLOAT,
                location=OpenApiParameter.QUERY,
                description="Maximum variant price",
            ),
            OpenApiParameter(
                name="sort",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Sorting option",
                enum=["newest", "price_asc", "price_desc"],
            ),
        ],
        responses={200: ProductListSerializer(many=True)},
    )
    def get(self, request):
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
                    queryset=ProductVariant.objects
                    .filter(is_active=True)
                    .select_related("inventory"),
                ),
            )
        )

        params = request.query_params

        # -------------------------
        # Category Filter
        # -------------------------
        if category := params.get("category"):
            queryset = queryset.filter(
                category__slug__iexact=category
            )

        # -------------------------
        # Size Filter
        # -------------------------
        if size := params.get("size"):
            queryset = queryset.filter(
                variants__size__iexact=size,
                variants__is_active=True
            ).distinct()

        # -------------------------
        # Price Range Filter
        # -------------------------
        min_price = params.get("min_price")
        max_price = params.get("max_price")

        if min_price:
            queryset = queryset.filter(
                variants__price__gte=min_price
            )

        if max_price:
            queryset = queryset.filter(
                variants__price__lte=max_price
            )

        # -------------------------
        # Sorting
        # -------------------------
        sort = params.get("sort")

        if sort == "newest":
            queryset = queryset.order_by("-created_at")

        elif sort == "price_asc":
            queryset = queryset.annotate(
                min_price=Min("variants__price")
            ).order_by("min_price")

        elif sort == "price_desc":
            queryset = queryset.annotate(
                min_price=Min("variants__price")
            ).order_by("-min_price")

        serializer = ProductListSerializer(
            queryset.distinct(),
            many=True,
            context={"request": request},
        )

        return Response(serializer.data, status=status.HTTP_200_OK)