from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.products.api.serializers.product_type_serializer import (
    ProductTypeSerializer
)


class AdminProductTypeCreateAPIView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=["Admin"],
        summary="Create Product Type",
        description="Creates a new product type (Admin only).",
        operation_id="admin_product_type_create",
        request=ProductTypeSerializer,
        responses={
            201: OpenApiResponse(
                description="Category created successfully",
                response=ProductTypeSerializer,
            ),
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
        },
    )

    def post(self, request):
        serializer = ProductTypeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_type = serializer.save()

        return Response(
            {
                "id": product_type.id,
                "slug": product_type.slug,
                "detail": "Product type created successfully"
            },
            status=status.HTTP_201_CREATED
        )
