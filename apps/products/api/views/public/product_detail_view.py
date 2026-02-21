from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from apps.products.models import Product
from apps.wishlist.models import WishlistItem
from apps.cart.models import CartItem
from apps.products.api.serializers.product_detail_serializer import ProductDetailSerializer


class ProductDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        product = get_object_or_404(
            Product.objects.select_related(
                "category",
                "product_type",
                "metrics",
            ).prefetch_related(
                "images",
                "features",
                "variants__inventory",
            ),
            slug=slug,
            is_active=True,
        )

        if request.user.is_authenticated:
            variant_ids = [v.id for v in product.variants.all()]

            wishlist_variant_ids = set(
                WishlistItem.objects.filter(
                    wishlist__user=request.user,
                    product_variant_id__in=variant_ids,
                ).values_list("product_variant_id", flat=True)
            )

            cart_variant_ids = set(
                CartItem.objects.filter(
                    cart__user=request.user,
                    variant_id__in=variant_ids,
                ).values_list("variant_id", flat=True)
            )
        else:
            wishlist_variant_ids = set()
            cart_variant_ids = set()

        serializer = ProductDetailSerializer(
            product,
            context={
                "request": request,
                "wishlist_variant_ids": wishlist_variant_ids,
                "cart_variant_ids": cart_variant_ids,
            },
        )

        return Response(serializer.data, status=status.HTTP_200_OK)