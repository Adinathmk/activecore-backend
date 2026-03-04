from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from django.db.models import Q
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from apps.orders.models import Order
from apps.orders.api.serializers import OrderSerializer


class AdminOrderSearchView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = (
            Order.objects
            .select_related("user")
            .prefetch_related("items")
            .order_by("-placed_at")
        )

        search_query = self.request.query_params.get("search")
        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query)
            )

        status_param = self.request.query_params.get("status")
        if status_param and status_param != "All":
            queryset = queryset.filter(status=status_param)

        return queryset

    @extend_schema(
        tags=["Orders-admin"],
        summary="Admin: Search Orders",
        description="Search orders by ID, email, or user name.",
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search by order ID, customer name, or email",
            ),
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by order status (PENDING, PROCESSING, SHIPPED, etc.)",
            ),
        ],
        responses={200: OrderSerializer(many=True)},
    )
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)
