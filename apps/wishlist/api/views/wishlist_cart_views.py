from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers

from apps.products.models import ProductVariant, Inventory
from apps.cart.models import Cart, CartItem
from ...models import Wishlist, WishlistItem


class MoveAllWishlistToCartView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Move all wishlist items to cart",
        responses={
            200: inline_serializer(
                name="MoveAllWishlistToCartResponse",
                fields={
                    "wishlist_count": serializers.IntegerField(),
                    "detail": serializers.CharField(),
                },
            ),
            400: OpenApiResponse(description="Wishlist empty or stock issue"),
        },
    )
    @transaction.atomic
    def post(self, request):
        user = request.user

        wishlist = Wishlist.objects.select_for_update().get(user=user)
        wishlist_items = list(
            WishlistItem.objects
            .select_related("product_variant__product")
            .select_for_update()
            .filter(wishlist=wishlist)
        )

        if not wishlist_items:
            return Response({"detail": "Wishlist is empty."}, status=400)

        cart, _ = Cart.objects.get_or_create(user=user)

        for item in wishlist_items:
            variant = item.product_variant

            if not variant.is_active or not variant.product.is_active:
                continue

            inventory = Inventory.objects.select_for_update().get(
                variant=variant
            )

            if inventory.available_stock < 1:
                return Response(
                    {"detail": f"{variant.product.name} out of stock"},
                    status=400
                )

            cart_item, created = CartItem.objects.select_for_update().get_or_create(
                cart=cart,
                variant=variant,
                defaults={
                    "quantity": 1,
                    "unit_price": variant.selling_price,
                    "discount_percent": variant.discount_percent,
                }
            )

            if not created:
                cart_item.quantity += 1
                cart_item.unit_price = variant.selling_price
                cart_item.discount_percent = variant.discount_percent
                cart_item.save()

        wishlist.items.all().delete()

        cart.recalculate_totals()

        return Response({
            "wishlist_count": 0,
            "detail": "All wishlist items moved to cart successfully."
        })