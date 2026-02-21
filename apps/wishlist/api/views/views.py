from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse,inline_serializer
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers

from apps.products.models import ProductVariant
from ...models import Wishlist, WishlistItem
from ..serializers import WishlistItemSerializer
from apps.products.models import Inventory


# ==============================
# Wishlist (List + Clear)
# ==============================

class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get user wishlist",
        description="Returns all wishlist items for the authenticated user",
        responses=WishlistItemSerializer(many=True),
    )
    def get(self, request):
        wishlist, created = Wishlist.objects.get_or_create(
            user=request.user
        )

        wishlist = Wishlist.objects.prefetch_related(
            Prefetch(
                "items",
                queryset=WishlistItem.objects.select_related(
                    "product_variant__product"
                )
            )
        ).get(pk=wishlist.pk)

        serializer = WishlistItemSerializer(
            wishlist.items.all(),
            many=True
        )

        return Response(serializer.data)

    @extend_schema(
        summary="Clear wishlist",
        description="Deletes all wishlist items for the authenticated user",
        responses={200: OpenApiResponse(description="Wishlist cleared")},
    )
    def delete(self, request):
        WishlistItem.objects.filter(
            wishlist__user=request.user
        ).delete()

        return Response({"cleared": True})


# ==============================
# Add Item
# ==============================

class WishlistItemCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Add item to wishlist",
        description="Adds a product variant to the user's wishlist",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "variant_id": {"type": "integer"},
                },
                "required": ["variant_id"],
            }
        },
        responses={
            201: OpenApiResponse(description="Item added"),
            200: OpenApiResponse(description="Item already exists"),
        },
    )
    @transaction.atomic
    def post(self, request):
        variant = get_object_or_404(
            ProductVariant,
            id=request.data.get("variant_id"),
            is_active=True
        )

        wishlist = request.user.wishlist

        item, created = WishlistItem.objects.get_or_create(
            wishlist=wishlist,
            product_variant=variant,
            defaults={"price_at_added": variant.price}
        )

        return Response(
            {"added": created},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


# ==============================
# Remove Item
# ==============================

class WishlistItemDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Remove item from wishlist",
        description="Removes a specific product variant from wishlist",
        parameters=[
            OpenApiParameter(
                name="variant_id",
                type=int,
                location=OpenApiParameter.PATH,
                required=True,
                description="Product Variant ID",
            )
        ],
        responses={200: OpenApiResponse(description="Item removed")},
    )
    def delete(self, request, variant_id):
        WishlistItem.objects.filter(
            wishlist__user=request.user,
            product_variant_id=variant_id
        ).delete()

        return Response({"removed": True})
    


class WishlistCountView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get wishlist item count",
        description="Returns total number of items in user's wishlist",
        responses={200: OpenApiResponse(description="Wishlist count")},
    )
    def get(self, request):
        count = WishlistItem.objects.filter(
            wishlist__user=request.user
        ).count()

        return Response({"count": count})



from apps.cart.models import Cart,CartItem





class MoveAllWishlistToCartView(APIView):
    """
    Move all wishlist items to cart (optimized & production safe).
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Move all wishlist items to cart",
        description=(
            "Moves all product variants from the user's wishlist "
            "to their shopping cart. Each item is validated against "
            "inventory before moving. If already present in cart, "
            "quantity is incremented."
        ),
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

        # 🔒 Lock all existing cart items at once
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

        wishlist_items and WishlistItem.objects.filter(
            id__in=[item.id for item in wishlist_items]
        ).delete()

        cart.recalculate_totals()

        return Response(
            {
                "wishlist_count": 0,
                "detail": "All wishlist items moved to cart successfully."
            }
        )