from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.accounts.models import User
from apps.accounts.permissions import IsAdminUserRole


class AdminUserBlockToggleView(APIView):
    permission_classes = [IsAdminUserRole]

    @extend_schema(
        tags=["Users-admin"],
        summary="Block or Unblock a User",
        description="Toggle user's active status. Admin users cannot be blocked.",
        responses={
            200: OpenApiResponse(
                description="User status updated successfully"
            ),
            400: OpenApiResponse(
                description="Cannot block admin or invalid request"
            ),
            404: OpenApiResponse(
                description="User not found"
            ),
        },
    )
    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        if user.role == User.Role.ADMIN:
            return Response(
                {"detail": "Cannot block another admin"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user == request.user:
            return Response(
                {"detail": "You cannot block yourself"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])

        return Response({
            "status": "Active" if user.is_active else "Blocked"
        })

# ----------------------------------------------------------------

class AdminUserDeleteView(APIView):
    permission_classes = [IsAdminUserRole]

    @extend_schema(
        tags=["Users-admin"],
        summary="Delete a User",
        description="Delete a customer user. Admin users cannot be deleted.",
        responses={
            204: OpenApiResponse(description="User deleted successfully"),
            400: OpenApiResponse(description="Cannot delete admin"),
            404: OpenApiResponse(description="User not found"),
        },
    )
    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        if user.role == User.Role.ADMIN:
            return Response(
                {"detail": "Cannot delete admin"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user == request.user:
            return Response(
                {"detail": "You cannot delete yourself"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)