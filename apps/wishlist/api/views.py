from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from apps.products.models import ProductVariant
from ..models import Wishlist, WishlistItem
from .serializers import WishlistItemSerializer


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