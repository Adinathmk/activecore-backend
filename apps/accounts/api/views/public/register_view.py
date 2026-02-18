# apps/accounts/views/register.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from drf_spectacular.utils import extend_schema
from apps.accounts.api.serializers.register_serializer import RegisterSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={201: dict, 400: dict},
        tags=["auth"],
        summary="Register a new user",
        description="Creates a new customer account and sends verification email"
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            {
                "detail": "Registration successful. Please verify your email."
            },
            status=status.HTTP_201_CREATED
        )
