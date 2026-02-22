from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from apps.products.models import Product
from apps.products.api.serializers.product_create_serializer import ProductCreateSerializer
from apps.products.api.serializers.admin_product_list_serializer import AdminProductListSerializer
from apps.products.api.serializers.admin_product_detail_serializer import AdminProductDetailSerializer


class AdminProductListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAdminUser]

    # -----------------------------
    # Dynamic Serializer Selection
    # -----------------------------
    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProductCreateSerializer
        return AdminProductListSerializer

    # -----------------------------
    # Queryset with Filtering
    # -----------------------------
    def get_queryset(self):
        queryset = (
            Product.objects
            .select_related("category", "product_type", "metrics")
            .order_by("-created_at")
        )

        is_active = self.request.query_params.get("is_active")
        category = self.request.query_params.get("category")
        product_type = self.request.query_params.get("product_type")
        search = self.request.query_params.get("search")

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        if category:
            queryset = queryset.filter(category_id=category)

        if product_type:
            queryset = queryset.filter(product_type_id=product_type)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        return queryset

    # -----------------------------
    # FIXED CREATE METHOD 🔥
    # -----------------------------
    def create(self, request, *args, **kwargs):
        serializer = ProductCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        # Return READ serializer instead of WRITE serializer
        response_serializer = AdminProductDetailSerializer(product)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )

    # -----------------------------
    # Swagger Documentation
    # -----------------------------
    @extend_schema(
        tags=["product-admin"],
        summary="Admin Product List",
        parameters=[
            OpenApiParameter(name="is_active", type=bool),
            OpenApiParameter(name="category", type=int),
            OpenApiParameter(name="product_type", type=int),
            OpenApiParameter(name="search", type=str),
        ],
        responses={200: AdminProductListSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["product-admin"],
        summary="Create Product",
        request=ProductCreateSerializer,
        responses={
            201: AdminProductDetailSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
