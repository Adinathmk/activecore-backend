from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser

from drf_spectacular.utils import extend_schema, OpenApiResponse

from ....services import OrderService
from ....models import Order
from ...serializers import OrderSerializer,AdminOrderStatusUpdateSerializer



class AdminOrderStatusUpdateView(APIView):
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        tags=["Orders-admin"],
        summary="Admin: Update order status",
        description="Allows admin users to update the status of an order.",
        request=AdminOrderStatusUpdateSerializer,
        responses={
            200: OrderSerializer,
            400: OpenApiResponse(description="Invalid status transition"),
            404: OpenApiResponse(description="Order not found"),
        },
    )
    def patch(self, request, pk):

        order = get_object_or_404(Order, pk=pk)

        serializer = AdminOrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = OrderService.update_status(
                order=order,
                new_status=serializer.validated_data["new_status"],
                changed_by=request.user,
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(OrderSerializer(order).data)