from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser

from drf_spectacular.utils import extend_schema, OpenApiResponse

from ..services import OrderService
from ..models import Order
from .serializers import OrderSerializer, CheckoutSerializer,AdminOrderStatusUpdateSerializer




class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Orders"],
        request=CheckoutSerializer,
        responses={
            201: OrderSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
        description="Create an order from the authenticated user's cart."
    )
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = OrderService.create_order(
            user=request.user,
            shipping_address=serializer.validated_data["shipping_address"],
            billing_address=serializer.validated_data["billing_address"],
        )

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )
    
class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Orders"],
        responses={200: OrderSerializer(many=True)},
        description="Retrieve all orders for the authenticated user."
    )
    def get(self, request):
        orders = request.user.orders.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Orders"],
        responses={
            200: OrderSerializer,
            404: OpenApiResponse(description="Order not found"),
        },
        description="Retrieve details of a specific order belonging to the authenticated user."
    )
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Orders"],
        responses={
            200: OrderSerializer,
            400: OpenApiResponse(description="Cannot cancel order"),
            404: OpenApiResponse(description="Order not found"),
        },
        description="Cancel an order if it belongs to the authenticated user."
    )
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        order = OrderService.cancel_order(order, request.user)
        return Response(OrderSerializer(order).data)



class AdminOrderStatusUpdateView(APIView):
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        tags=["Admin Orders"],
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