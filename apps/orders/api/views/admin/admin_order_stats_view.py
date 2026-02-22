from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from drf_spectacular.utils import extend_schema,OpenApiTypes
from rest_framework.permissions import IsAdminUser
from apps.orders.models import Order


class AdminOrderStatsView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=["Orders-admin"],
        summary="Admin: Order Statistics",
        description="Returns count of orders grouped by status.",
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        data = (
            Order.objects
            .values("status")
            .annotate(count=Count("id"))
        )
        return Response(data)