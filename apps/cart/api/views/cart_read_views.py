from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema, OpenApiResponse

from ...models import Cart, CartItem
from ..serializers import CartSerializer


@extend_schema(
    summary="Retrieve authenticated user's cart",
    description="Returns the active cart of the authenticated user including all cart items and totals.",
    responses={
        200: CartSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        404: OpenApiResponse(description="Cart not found."),
    },
    tags=["cart"],
)
class CartDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_object(self):
        try:
            return (
                Cart.objects
                .prefetch_related(
                    Prefetch(
                        "items",
                        queryset=CartItem.objects.select_related(
                            "variant__product",
                            "variant__inventory",
                        ).prefetch_related(
                            "variant__product__images"
                        )
                    )
                )
                .get(user=self.request.user)
            )
        except Cart.DoesNotExist:
            raise NotFound("Cart not found.")