from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.products.models import ProductVariant, Inventory
from ...models import Cart, CartItem
from ..serializers import CartSerializer, UpdateCartItemSerializer



@extend_schema(
    summary="Add product variant to cart",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "variant_id": {"type": "integer"},
                "quantity": {"type": "integer", "minimum": 1},
            },
            "required": ["variant_id"],
        }
    },
    responses={200: CartSerializer},
)
class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):

        variant_id = request.data.get("variant_id")
        quantity = int(request.data.get("quantity", 1))

        variant = get_object_or_404(
            ProductVariant.objects.select_for_update(),
            id=variant_id,
            is_active=True,
            product__is_active=True
        )

        inventory = Inventory.objects.select_for_update().get(
            variant=variant
        )

        if inventory.available_stock < quantity:
            return Response(
                {"detail": "Insufficient stock"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart, _ = Cart.objects.get_or_create(user=request.user)

        item, created = CartItem.objects.select_for_update().get_or_create(
            cart=cart,
            variant=variant,
            defaults={
                "quantity": quantity,
                "unit_price": variant.selling_price,
                "discount_percent": variant.discount_percent
            }
        )

        if not created:
            if inventory.available_stock < (item.quantity + quantity):
                return Response(
                    {"detail": "Insufficient stock"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            item.quantity += quantity
            item.save()

        cart.recalculate_totals()

        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_200_OK
        )
    

# -----------------------------------------------------


@extend_schema(
    summary="Update cart item quantity",
    tags=["cart"],
)
class UpdateCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def patch(self, request, item_id):

        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_quantity = serializer.validated_data["quantity"]

        cart = request.user.cart

        cart_item = get_object_or_404(
            CartItem.objects.select_for_update(),
            id=item_id,
            cart=cart
        )

        variant = cart_item.variant

        inventory = Inventory.objects.select_for_update().get(
            variant_id=variant.id
        )

        if new_quantity == 0:
            cart_item.delete()
            cart.recalculate_totals()
            return Response(CartSerializer(cart).data)

        if not variant.is_active or not variant.product.is_active:
            return Response(
                {"detail": "Product is no longer available."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if inventory.available_stock < new_quantity:
            return Response(
                {"detail": "Insufficient stock available."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = new_quantity
        cart_item.unit_price = variant.selling_price
        cart_item.discount_percent = variant.discount_percent
        cart_item.save()

        cart.recalculate_totals()

        return Response(CartSerializer(cart).data)
    

# ---------------------------------------------------------------------

class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request, item_id):

        cart, _ = Cart.objects.get_or_create(user=request.user)

        cart_item = get_object_or_404(
            CartItem.objects.select_for_update(),
            id=item_id,
            cart=cart
        )

        cart_item.delete()

        cart.recalculate_totals()

        return Response(CartSerializer(cart).data)
    

# ---------------------------------------------------------------------------


class ClearCartView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request):

        try:
            cart = request.user.cart
        except Cart.DoesNotExist:
            return Response(
                {"detail": "Cart not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        cart = Cart.objects.select_for_update().get(pk=cart.pk)

        cart.items.all().delete()

        cart.subtotal = 0
        cart.tax_amount = 0
        cart.shipping_amount = 0
        cart.total_amount = 0
        cart.save(update_fields=[
            "subtotal",
            "tax_amount",
            "shipping_amount",
            "total_amount",
            "updated_at"
        ])

        return Response(CartSerializer(cart).data)
    

# ---------------------------------------------------------------------------


class ClearCartView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request):

        try:
            cart = request.user.cart
        except Cart.DoesNotExist:
            return Response(
                {"detail": "Cart not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        cart = Cart.objects.select_for_update().get(pk=cart.pk)

        cart.items.all().delete()

        cart.subtotal = 0
        cart.tax_amount = 0
        cart.shipping_amount = 0
        cart.total_amount = 0
        cart.save(update_fields=[
            "subtotal",
            "tax_amount",
            "shipping_amount",
            "total_amount",
            "updated_at"
        ])

        return Response(CartSerializer(cart).data)