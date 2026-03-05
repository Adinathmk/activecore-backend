from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.products.models import Product
from apps.products.api.serializers.admin_product_detail_serializer import (
    AdminProductDetailSerializer,
)
from apps.products.api.serializers.product_update_serializer import (
    ProductFullUpdateSerializer,
)


class AdminProductRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [IsAdminUser]


    def get_object(self, pk):
        return get_object_or_404(
            Product.objects
            .select_related("category", "product_type", "metrics")
            .prefetch_related(
                "images",
                "features",
                "variants__inventory",
                "ratings",
            ),
            pk=pk
        )

    @extend_schema(
        tags=["product-admin"],
        summary="Retrieve Complete Product Detail",
        responses={200: AdminProductDetailSerializer},
    )
    def get(self, request, pk):
        product = self.get_object(pk)

        serializer = AdminProductDetailSerializer(
            product,
            context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["product-admin"],
        summary="Update Product",
        request=ProductFullUpdateSerializer,
        responses={200: AdminProductDetailSerializer},
    )
    @transaction.atomic
    def patch(self, request, pk):
        product = self.get_object(pk)

        from apps.products.utils import parse_multipart_data
        parsed_data = parse_multipart_data(request.data)
        
        # Merge uploaded files into parsed_data images
        images_data = parsed_data.get("images", [])
        if not isinstance(images_data, list):
            images_data = []

        for key, file in request.FILES.items():
            if key.startswith("images[") and key.endswith("][image]"):
                try:
                    index = int(key.split("[")[1].split("]")[0])
                    while len(images_data) <= index:
                        images_data.append({})
                    images_data[index]["image"] = file
                except (IndexError, ValueError):
                    pass
        
        parsed_data["images"] = images_data

        write_serializer = ProductFullUpdateSerializer(
            product,
            data=parsed_data,
            partial=True
        )
        write_serializer.is_valid(raise_exception=True)
        write_serializer.save()

       
        read_serializer = AdminProductDetailSerializer(
            product,
            context={"request": request}
        )

        return Response(read_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["product-admin"],
        summary="Soft Delete Product",
        responses={
            204: OpenApiResponse(description="Product deactivated"),
            400: OpenApiResponse(description="Already inactive"),
        },
    )
    @transaction.atomic
    def delete(self, request, pk):
        product = self.get_object(pk)

        if not product.is_active:
            return Response(
                {"detail": "Product already inactive."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        
        product.is_active = False
        product.save(update_fields=["is_active"])

        
        product.variants.update(is_active=False)

        return Response(
            {"detail": "Product deactivated successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
