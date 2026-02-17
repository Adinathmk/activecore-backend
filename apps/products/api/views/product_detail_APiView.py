from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from apps.products.models import Product
from apps.products.api.serializers.ProductDetailSerializer import ProductDetailSerializer


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

        serializer = ProductDetailSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)
