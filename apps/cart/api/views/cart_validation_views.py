from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from apps.products.models import Inventory
from ...models import Cart
from ..serializers import CartSerializer



@extend_schema(
    summary="Validate cart before checkout",
    tags=["cart"],
)
class ValidateCartView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):

        try:
            cart = request.user.cart
        except Cart.DoesNotExist:
            return Response(
                {"detail": "Cart not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not cart.items.exists():
            return Response(
                {"detail": "Cart is empty."},
                status=status.HTTP_400_BAD_REQUEST
            )

        errors = []
        price_updated = False

        for item in cart.items.select_related("variant__product"):

            variant = item.variant

            inventory = Inventory.objects.select_for_update().get(
                variant_id=variant.id
            )

            if not variant.is_active or not variant.product.is_active:
                errors.append({
                    "item_id": item.id,
                    "error": "Product no longer available."
                })
                continue

            if inventory.available_stock < item.quantity:
                errors.append({
                    "item_id": item.id,
                    "error": "Insufficient stock."
                })
                continue

            current_price = variant.selling_price

            if item.unit_price != current_price:
                item.unit_price = current_price
                item.discount_percent = variant.discount_percent
                item.save()
                price_updated = True

        if errors:
            return Response(
                {"status": "failed", "errors": errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart.recalculate_totals()

        return Response(
            {
                "status": "valid",
                "price_updated": price_updated,
                "cart": CartSerializer(cart).data
            }
        )