from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.products.api.serializers.category_serializer import (
    CategorySerializer
)
from apps.products.models import Category


class AdminCategoryCreateAPIView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=["product-admin"],
        summary="Create Category",
        description="Creates a new product category (Admin only).",
        request=CategorySerializer,
        responses={
            201: OpenApiResponse(
                description="Category created successfully",
                response=CategorySerializer,
            ),
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
        },
    )

    @extend_schema(
        tags=["product-admin"],
        summary="List Categories",
        description="Retrieves all product categories (Admin only).",
        responses={200: CategorySerializer(many=True)},
    )
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()

        return Response(
            {
                "id": category.id,
                "slug": category.slug,
                "detail": "Category created successfully"
            },
            status=status.HTTP_201_CREATED
        )
