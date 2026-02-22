from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from ...models import WishlistItem


class WishlistCountView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get wishlist item count",
        responses={200: OpenApiResponse(description="Wishlist count")},
    )
    def get(self, request):
        count = WishlistItem.objects.filter(
            wishlist__user=request.user
        ).count()

        return Response({"count": count})