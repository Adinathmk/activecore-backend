from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
)

from ....models import Order
from ....services import StripeService


class CreatePaymentIntentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Payments"],
        summary="Create Stripe PaymentIntent",
        description=(
            "Creates a Stripe PaymentIntent for the specified order. "
            "Order must be in PENDING state. "
            "Returns clientSecret used by frontend to confirm payment."
        ),
        request=None,  # No request body required
        responses={
            200: OpenApiResponse(
                description="Client secret returned successfully",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={
                            "clientSecret": "pi_3Nxxxxx_secret_xxxxx"
                        },
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Invalid order state",
                examples=[
                    OpenApiExample(
                        "Already Paid",
                        value={"error": "Payment already processed"},
                    )
                ],
            ),
            404: OpenApiResponse(description="Order not found"),
        },
    )
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)

        if order.status != "PENDING":
            return Response(
                {"error": "Payment already processed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        intent = StripeService.create_payment_intent(order)

        return Response({
            "clientSecret": intent.client_secret
        })