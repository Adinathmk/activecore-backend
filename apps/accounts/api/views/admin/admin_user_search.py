# apps/accounts/api/views/admin/admin_user_search.py

from rest_framework.generics import ListAPIView
from django.db.models import Value, CharField
from django.db.models.functions import Concat
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.accounts.models import User
from apps.accounts.permissions import IsAdminUserRole
from apps.accounts.api.serializers.admin_user_list_serializer import (
    AdminUserListSerializer,
)


@extend_schema(
    tags=["Users-admin"],
    summary="Search Users by Full Name",
    description="Retrieve paginated list of users filtered by full name.",
    parameters=[
        OpenApiParameter(
            name="name",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search by exact or partial full name (first_name + ' ' + last_name)",
            required=True
        ),
    ],
    responses={200: AdminUserListSerializer(many=True)},
)
class AdminUserSearchByNameView(ListAPIView):
    serializer_class = AdminUserListSerializer
    permission_classes = [IsAdminUserRole]

    def get_queryset(self):
        queryset = User.objects.annotate(
            full_name_search=Concat(
                "first_name",
                Value(" "),
                "last_name",
                output_field=CharField(),
            )
        )

        name_query = self.request.query_params.get("name", "").strip()

        if name_query:
            queryset = queryset.filter(
                full_name_search__icontains=name_query
            )
        else:
            queryset = queryset.none()

        return queryset.order_by("-date_joined")