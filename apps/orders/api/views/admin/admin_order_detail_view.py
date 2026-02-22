from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import IsAdminUser
from apps.orders.api.serializers import OrderSerializer
from apps.orders.models import Order
from rest_framework import generics


class AdminOrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = OrderSerializer
    lookup_field = "pk"

    def get_queryset(self):
        return (
            Order.objects
            .select_related("user")
            .prefetch_related("items", "status_history")
        )

    @extend_schema(
        tags=["Orders-admin"],
        summary="Admin: Order Detail",
        description="Retrieve full details of a specific order.",
        responses={
            200: OrderSerializer,
            404: OpenApiResponse(description="Order not found"),
        },
    )
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)