from rest_framework import generics, filters
from rest_framework.permissions import IsAdminUser
from django.db.models import Q
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from apps.orders.models import Order
from apps.orders.api.serializers import OrderSerializer


class AdminOrderListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = OrderSerializer

    # Only DRF Search + Ordering
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["id", "user__email", "user__first_name", "user__last_name"]
    ordering_fields = ["placed_at", "total_amount"]
    ordering = ["-placed_at"]

    def get_queryset(self):
        queryset = (
            Order.objects
            .select_related("user")
            .prefetch_related("items")
            .all()
        )

        # ✅ Manual status filter
        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset

    @extend_schema(
        tags=["Orders-admin"],
        summary="Admin: List Orders",
        description="Retrieve all orders with optional filtering by status, search, and ordering.",
        parameters=[
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by order status (PENDING, PROCESSING, SHIPPED, etc.)",
            ),
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search by order ID, customer name, or email",
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Order by placed_at or total_amount. Prefix with '-' for descending.",
            ),
        ],
        responses={200: OrderSerializer(many=True)},
    )
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)