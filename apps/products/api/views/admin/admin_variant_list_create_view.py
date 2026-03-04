from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from django.db.models import Q

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from apps.products.models import ProductVariant
from apps.products.api.serializers.admin_variant_serializer import (
    AdminVariantListSerializer,
    AdminVariantCreateUpdateSerializer
)


class AdminVariantListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]

    queryset = ProductVariant.objects.select_related(
        "product",
        "inventory"
    ).all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AdminVariantCreateUpdateSerializer
        return AdminVariantListSerializer

    def get_queryset(self):
        queryset = self.queryset

        # Filter by product
        product_id = self.request.query_params.get("product_id")
        if product_id:
            queryset = queryset.filter(product_id=product_id)

        # Search by SKU or product name
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(sku__icontains=search) |
                Q(product__name__icontains=search)
            )

        return queryset

    @extend_schema(
        tags=["inventory-admin"],
        summary="List Variants (Inventory)",
        description="Retrieve all product variants and their inventory stock.",
        parameters=[
            OpenApiParameter(
                name="product_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY
            ),
        ],
        responses={200: AdminVariantListSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["inventory-admin"],
        summary="Create Variant",
        description="Creates a new variant and its associated inventory record.",
        request=AdminVariantCreateUpdateSerializer,
        responses={201: AdminVariantCreateUpdateSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)