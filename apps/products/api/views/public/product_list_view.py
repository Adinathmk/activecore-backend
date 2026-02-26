from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from django.db.models import Prefetch, Min

from drf_spectacular.utils import (
    extend_schema,

)

from apps.products.models import Product, ProductVariant, ProductImage
from apps.products.api.serializers.product_list_serializer import (
    ProductListSerializer
)
from apps.wishlist.models import WishlistItem
from apps.cart.models import CartItem


class ProductListAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["products"],
        summary="List products with filters and sorting",
        responses={200: ProductListSerializer(many=True)},
    )
    def get(self, request):

        # -------------------------
        # Base Query
        # -------------------------
        queryset = (
            Product.objects
            .filter(is_active=True)
            .select_related("category", "product_type")
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=ProductImage.objects.order_by("order"),
                ),
                Prefetch(
                    "variants",
                    queryset=ProductVariant.objects
                    .filter(is_active=True)
                    .select_related("inventory"),
                ),
            )
        )

        params = request.query_params

        # -------------------------
        # Category Filter
        # -------------------------
        if category := params.get("category"):
            queryset = queryset.filter(
                category__slug__iexact=category
            )

        # -------------------------
        # Size Filter
        # -------------------------
        if size := params.get("size"):
            queryset = queryset.filter(
                variants__size__iexact=size,
                variants__is_active=True
            ).distinct()

        # -------------------------
        # Price Filters
        # -------------------------
        min_price = params.get("min_price")
        max_price = params.get("max_price")

        if min_price:
            queryset = queryset.filter(
                variants__selling_price__gte=min_price,
                variants__is_active=True
            )

        if max_price:
            queryset = queryset.filter(
                variants__selling_price__lte=max_price,
                variants__is_active=True
            )

        # -------------------------
        # Sorting
        # -------------------------
        sort = params.get("sort")

        if sort == "newest":
            queryset = queryset.order_by("-created_at")

        elif sort == "price_asc":
            queryset = queryset.annotate(
                min_price=Min(
                    "variants__selling_price",
                    filter=models.Q(variants__is_active=True)
                )
            ).order_by("min_price")

        elif sort == "price_desc":
            queryset = queryset.annotate(
                min_price=Min(
                    "variants__selling_price",
                    filter=models.Q(variants__is_active=True)
                )
            ).order_by("-min_price")

        # -------------------------
        # Wishlist & Cart
        # -------------------------
        if request.user.is_authenticated:
            wishlist_variant_ids = set(
                WishlistItem.objects.filter(
                    wishlist__user=request.user
                ).values_list("product_variant_id", flat=True)
            )

            cart_variant_ids = set(
                CartItem.objects.filter(
                    cart__user=request.user
                ).values_list("variant_id", flat=True)
            )
        else:
            wishlist_variant_ids = set()
            cart_variant_ids = set()

        # -------------------------
        # Serialize
        # -------------------------
        serializer = ProductListSerializer(
            queryset.distinct(),
            many=True,
            context={
                "request": request,
                "wishlist_variant_ids": wishlist_variant_ids,
                "cart_variant_ids": cart_variant_ids,
            },
        )

        return Response(serializer.data, status=status.HTTP_200_OK)