from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema, OpenApiResponse

from ...models import Wishlist, WishlistItem
from ..serializers import WishlistItemSerializer


class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get user wishlist",
        description="Returns all wishlist items for the authenticated user",
        responses=WishlistItemSerializer(many=True),
    )
    def get(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

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