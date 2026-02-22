
from rest_framework.generics import RetrieveAPIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.accounts.models import User
from apps.accounts.permissions import IsAdminUserRole
from apps.accounts.api.serializers.admin_user_detail_serializer import (
    AdminUserDetailSerializer,
)


@extend_schema(
    tags=["Users-admin"],
    summary="Retrieve User Details",
    description="Retrieve detailed information of a specific user including statistics like wishlist, cart, and order count.",
    responses={
        200: AdminUserDetailSerializer,
        404: OpenApiResponse(description="User not found"),
    },
)
class AdminUserDetailView(RetrieveAPIView):
    serializer_class = AdminUserDetailSerializer
    permission_classes = [IsAdminUserRole]
    lookup_field = "pk"

    def get_queryset(self):
        return User.objects.all()