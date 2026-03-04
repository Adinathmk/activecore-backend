from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from django.db.models import Q

from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.products.models import Product
from apps.products.api.serializers.admin_product_list_serializer import AdminProductListSerializer


class AdminProductSearchAPIView(ListAPIView):
    """
    Dedicated admin product search endpoint.
    Searches across name, description, category name, and product type name.
    """
    serializer_class = AdminProductListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = (
            Product.objects
            .select_related("category", "product_type", "metrics")
            .order_by("-created_at")
        )

        search = self.request.query_params.get("search", "").strip()

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(category__name__icontains=search) |
                Q(product_type__name__icontains=search)
            )

        return queryset

    @extend_schema(
        tags=["product-admin"],
        summary="Admin Product Search",
        parameters=[
            OpenApiParameter(name="search", type=str, description="Search term"),
        ],
        responses={200: AdminProductListSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
