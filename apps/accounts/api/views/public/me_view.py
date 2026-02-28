from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema

from apps.accounts.api.serializers.user_serializer import UserSerializer
from apps.accounts.api.serializers.profile_serializer import UpdateProfileSerializer
from rest_framework.parsers import MultiPartParser, FormParser


class MeView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        tags=["profile"],
        summary="Get current user profile",
        description="Returns the authenticated user's profile details including address",
        responses={200: UserSerializer},
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        tags=["profile"],
        summary="Update current user profile",
        description="Update profile fields such as name, phone number, profile image and address",
        request=UpdateProfileSerializer,
        responses={200: UserSerializer},
    )
    def patch(self, request):
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            UserSerializer(request.user).data,
            status=status.HTTP_200_OK
        )