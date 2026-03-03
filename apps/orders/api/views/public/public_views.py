from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema, OpenApiResponse

from ....services import OrderService
from ....models import Order
from ...serializers import (
    OrderSerializer,
    CheckoutSerializer,
    AccountOverviewSerializer,
)

from django.db.models import Count, Sum, Q


# ==========================================================
# CHECKOUT
# ==========================================================

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Orders"],
        request=CheckoutSerializer,
        responses={
            201: OrderSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
        description="Checkout from cart OR buy single product directly.",
    )
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        variant_id = serializer.validated_data.get("variant_id")
        quantity = serializer.validated_data.get("quantity")
        payment_method = serializer.validated_data["payment_method"]

        try:
            if variant_id:
                order = OrderService.create_single_product_order(
                    user=request.user,
                    variant_id=variant_id,
                    quantity=quantity,
                    shipping_address=serializer.validated_data["shipping_address"],
                    billing_address=serializer.validated_data["billing_address"],
                    payment_method=payment_method,
                )
            else:
                order = OrderService.create_order(
                    user=request.user,
                    shipping_address=serializer.validated_data["shipping_address"],
                    billing_address=serializer.validated_data["billing_address"],
                    payment_method=payment_method,  # ✅ FIXED
                )

        except ValidationError as e:
            return Response(
                {"error": str(e.detail[0]) if hasattr(e, "detail") else str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# ORDER LIST
# ==========================================================

class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Orders"],
        responses={200: OrderSerializer(many=True)},
        description="Retrieve all orders for the authenticated user.",
    )
    def get(self, request):
        orders = (
            request.user.orders
            .prefetch_related("items")
            .order_by("-placed_at")
        )
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


# ==========================================================
# ORDER DETAIL
# ==========================================================

class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Orders"],
        responses={
            200: OrderSerializer,
            404: OpenApiResponse(description="Order not found"),
        },
        description="Retrieve details of a specific order belonging to the authenticated user.",
    )
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)


# ==========================================================
# CANCEL ORDER
# ==========================================================

class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Orders"],
        responses={
            200: OrderSerializer,
            400: OpenApiResponse(description="Cannot cancel order"),
            404: OpenApiResponse(description="Order not found"),
        },
        description="Cancel an order if it belongs to the authenticated user.",
    )
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)

        try:
            order = OrderService.cancel_order(order, request.user)
        except ValidationError as e:
            return Response(
                {"error": str(e.detail[0]) if hasattr(e, "detail") else str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(OrderSerializer(order).data)


# ==========================================================
# ACCOUNT OVERVIEW
# ==========================================================

class AccountOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Orders"],
        summary="Account Overview",
        description="Returns summary statistics for the authenticated user's account.",
        responses={200: AccountOverviewSerializer},
    )
    def get(self, request):

        user_orders = Order.objects.filter(user=request.user)

        stats = user_orders.aggregate(
            total_orders=Count("id"),
            confirmed_orders=Count("id", filter=Q(status="CONFIRMED")),
            delivered_orders=Count("id", filter=Q(status="DELIVERED")),
            cancelled_orders=Count("id", filter=Q(status="CANCELLED")),
            total_spent=Sum("total_amount", filter=Q(is_paid=True)),  # ✅ FIXED
        )

        stats["total_spent"] = stats["total_spent"] or 0

        serializer = AccountOverviewSerializer(stats)
        return Response(serializer.data)