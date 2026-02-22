from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from apps.products.models import ProductVariant
from ...models import Wishlist, WishlistItem


class WishlistItemCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Add item to wishlist",
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

        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

        item, created = WishlistItem.objects.get_or_create(
            wishlist=wishlist,
            product_variant=variant,
            defaults={"price_at_added": variant.price}
        )

        return Response(
            {"added": created},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


# -------------------------------------------------------------------------------

class WishlistItemDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Remove item from wishlist",
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