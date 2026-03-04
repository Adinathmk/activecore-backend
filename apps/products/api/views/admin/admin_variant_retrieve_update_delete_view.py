from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from apps.products.models import ProductVariant
from apps.products.api.serializers.admin_variant_serializer import (
    AdminVariantListSerializer,
    AdminVariantCreateUpdateSerializer
)


class AdminVariantRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    lookup_field = "id"

    queryset = ProductVariant.objects.select_related(
        "product", "inventory"
    ).all()

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return AdminVariantCreateUpdateSerializer
        return AdminVariantListSerializer

    @extend_schema(
        tags=["inventory-admin"],
        summary="Retrieve Variant",
        description="Retrieve a detailed view of a product variant.",
        responses={200: AdminVariantListSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["inventory-admin"],
        summary="Update Variant completely",
        description="Overwrite an existing variant and its inventory stock.",
        request=AdminVariantCreateUpdateSerializer,
        responses={200: AdminVariantCreateUpdateSerializer},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=["inventory-admin"],
        summary="Update Variant partially",
        description="Partially update an existing variant and its inventory stock.",
        request=AdminVariantCreateUpdateSerializer,
        responses={200: AdminVariantCreateUpdateSerializer},
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        tags=["inventory-admin"],
        summary="Deactivate Variant",
        description="Soft delete a variant by setting is_active=False.",
        responses={200: None},
    )
    def destroy(self, request, *args, **kwargs):
        variant = self.get_object()

        variant.is_active = False
        variant.save(update_fields=["is_active"])

        return Response(
            {"message": "Variant deactivated successfully."},
            status=status.HTTP_200_OK
        )