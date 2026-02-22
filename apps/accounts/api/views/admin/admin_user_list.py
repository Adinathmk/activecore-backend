# apps/accounts/api/views/admin/admin_user_list.py

from rest_framework.generics import ListAPIView
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.accounts.models import User
from apps.accounts.permissions import IsAdminUserRole
from apps.accounts.api.serializers.admin_user_list_serializer import (
    AdminUserListSerializer,
)


@extend_schema(
    tags=["Users-admin"],
    summary="List Users",
    description="Retrieve paginated list of users with optional search and role filtering.",
    parameters=[
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search by email, first name or last name",
        ),
        OpenApiParameter(
            name="role",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by role (admin or customer)",
        ),
        OpenApiParameter(
            name="ordering",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Order by date_joined (e.g. -date_joined)",
        ),
    ],
    responses={200: AdminUserListSerializer(many=True)},
)
class AdminUserListView(ListAPIView):
    serializer_class = AdminUserListSerializer
    permission_classes = [IsAdminUserRole]

    def get_queryset(self):
        queryset = User.objects.all().order_by("-date_joined")

        # 🔍 Search
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )

        # 🎭 Role filter (safe validation)
        role = self.request.query_params.get("role")
        if role in dict(User.Role.choices):
            queryset = queryset.filter(role=role)

        # 🔽 Ordering
        ordering = self.request.query_params.get("ordering")
        if ordering in ["date_joined", "-date_joined"]:
            queryset = queryset.order_by(ordering)

        return queryset