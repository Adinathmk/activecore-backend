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
            .select_for_update()
            .filter(wishlist=wishlist)
        )

        if not wishlist_items:
            return Response({"detail": "Wishlist is empty."}, status=400)

        variant_ids = [item.product_variant_id for item in wishlist_items]

        variants = (
            ProductVariant.objects
            .select_for_update()
            .filter(id__in=variant_ids, is_active=True, product__is_active=True)
        )
        variant_map = {v.id: v for v in variants}

        inventories = (
            Inventory.objects
            .select_for_update()
            .filter(variant_id__in=variant_ids)
        )
        inventory_map = {inv.variant_id: inv for inv in inventories}

        cart, _ = Cart.objects.get_or_create(user=user)

        existing_cart_items = (
            CartItem.objects
            .select_for_update()
            .filter(cart=cart, variant_id__in=variant_ids)
        )
        cart_item_map = {item.variant_id: item for item in existing_cart_items}

        items_to_create = []
        items_to_update = []

        for item in wishlist_items:
            variant = variant_map.get(item.product_variant_id)
            inventory = inventory_map.get(item.product_variant_id)

            if not variant or not inventory:
                continue

            if inventory.available_stock < 1:
                return Response(
                    {"detail": f"{variant.product.name} out of stock"},
                    status=400
                )

            existing_item = cart_item_map.get(variant.id)

            if existing_item:
                existing_item.quantity += 1
                existing_item.unit_price = variant.selling_price
                existing_item.discount_percent = variant.discount_percent
                items_to_update.append(existing_item)
            else:
                items_to_create.append(
                    CartItem(
                        cart=cart,
                        variant=variant,
                        quantity=1,
                        unit_price=variant.selling_price,
                        discount_percent=variant.discount_percent,
                    )
                )

        if items_to_create:
            CartItem.objects.bulk_create(items_to_create)

        if items_to_update:
            CartItem.objects.bulk_update(
                items_to_update,
                ["quantity", "unit_price", "discount_percent"]
            )

        WishlistItem.objects.filter(
            id__in=[item.id for item in wishlist_items]
        ).delete()

        cart.recalculate_totals()

        return Response(
            {
                "wishlist_count": 0,
                "detail": "All wishlist items moved to cart successfully."
            }
        )