from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiResponse
)

from rest_framework import serializers

from ..models import Notification
from ..services import notify_all_users


class NotificationListView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get user notifications",
        description="Returns the authenticated user's notifications ordered by newest first.",
        responses=inline_serializer(
            name="NotificationListResponse",
            many=True,
            fields={
                "id": serializers.UUIDField(),
                "message": serializers.CharField(),
                "is_read": serializers.BooleanField(),
                "created_at": serializers.DateTimeField(),
            },
        ),
    )
    def get(self, request):
        user_id = request.query_params.get("user_id")
        
        # If user_id is provided and requestor is admin, filter by that user
        if user_id and request.user.role == "admin":
            notifications = Notification.objects.filter(
                user_id=user_id
            ).order_by("-created_at")
        else:
            # Otherwise return current user's notifications
            notifications = Notification.objects.filter(
                user=request.user
            ).order_by("-created_at")

        data = [
            {
                "id": str(n.id),
                "message": n.message,
                "is_read": n.is_read,
                "created_at": n.created_at,
            }
            for n in notifications
        ]

        return Response(data, status=status.HTTP_200_OK)


class SendGlobalNotificationView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Send notification to all users",
        description="Creates a notification for all users and broadcasts it through WebSockets.",
        request=inline_serializer(
            name="SendNotificationRequest",
            fields={
                "message": serializers.CharField()
            },
        ),
        responses={
            200: inline_serializer(
                name="SendNotificationResponse",
                fields={
                    "status": serializers.CharField()
                },
            ),
            400: OpenApiResponse(description="Message is required"),
        },
    )
    def post(self, request):

        message = request.data.get("message")

        if not message:
            return Response(
                {"error": "Message is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        notify_all_users(message)

        return Response(
            {"status": "notification sent"},
            status=status.HTTP_200_OK
        )

from ..services import notify_user
from django.contrib.auth import get_user_model
User = get_user_model()

class SendUserNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Send notification to a specific user",
        description="Creates a notification for a target user and broadcasts it through WebSockets.",
        request=inline_serializer(
            name="SendUserNotificationRequest",
            fields={
                "user_id": serializers.UUIDField(),
                "message": serializers.CharField()
            },
        ),
        responses={
            200: inline_serializer(
                name="SendUserNotificationResponse",
                fields={
                    "status": serializers.CharField()
                },
            ),
            404: OpenApiResponse(description="User not found"),
        },
    )
    def post(self, request):
        if request.user.role != "admin":
            return Response({"detail": "Admin access required"}, status=403)

        user_id = request.data.get("user_id")
        message = request.data.get("message")

        try:
            target_user = User.objects.get(id=user_id)
            notify_user(target_user, message)
            return Response({"status": "notification sent to user"})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)