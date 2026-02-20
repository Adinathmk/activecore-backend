from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.products.models import Product
from apps.products.api.serializers.product_rating_create_serializer import (
    ProductRatingCreateSerializer
)


class ProductRatingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["products"],
        summary="Create or update product rating",
        description=(
            "Allows an authenticated user to rate a product "
            "(1–5). If the user has already rated, it updates the rating. "
            "Product metrics are recalculated automatically."
        ),
        request=ProductRatingCreateSerializer,
        responses={
            201: OpenApiResponse(description="Rating submitted successfully."),
            400: OpenApiResponse(description="Invalid rating input."),
            401: OpenApiResponse(description="Authentication required."),
            404: OpenApiResponse(description="Product not found."),
        },
    )
    def post(self, request, slug):
        product = get_object_or_404(
            Product,
            slug=slug,
        )

        serializer = ProductRatingCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "product": product,
            }
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Rating submitted successfully."},
            status=status.HTTP_201_CREATED
        )