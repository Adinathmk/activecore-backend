from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum


class CartCountView(APIView):
    """
    Returns total quantity of items in user's cart.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = getattr(request.user, "cart", None)

        if not cart:
            return Response({"count": 0})

        total_quantity = cart.items.aggregate(
            total=Sum("quantity")
        )["total"] or 0

        return Response({"count": total_quantity})