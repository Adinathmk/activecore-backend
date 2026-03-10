from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)

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
            "Order must be eligible for online payment. "
            "Returns clientSecret used by frontend to confirm payment."
        ),
        request=None,
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
                description="Invalid order state or payment not allowed",
                examples=[
                    OpenApiExample(
                        "Invalid Order",
                        value={"error": "Order is not eligible for payment"},
                    )
                ],
            ),
            404: OpenApiResponse(description="Order not found"),
        },
    )
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)

        try:
            intent = StripeService.create_payment_intent(order)
            logger.info(f"Payment intent created for Order {order.id} by User {request.user.id}")

        except ValidationError as e:
            
            error_message = (
                e.detail[0] if hasattr(e, "detail") else str(e)
            )

            return Response(
                {"error": error_message},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception:
            return Response(
                {"error": "Unable to create payment intent"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"clientSecret": intent.client_secret},
            status=status.HTTP_200_OK
        )