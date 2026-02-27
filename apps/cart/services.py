from decimal import Decimal
from apps.cart.models import CartItem
from core.pricing import PricingEngine


class CartService:

    @staticmethod
    def get_cart_summary(user):

        cart_items = (
            CartItem.objects
            .select_related("variant")
            .filter(cart__user=user)
        )

        subtotal = Decimal("0.00")
        item_count = 0

        for item in cart_items:
            subtotal += item.total_price
            item_count += item.quantity

        pricing = PricingEngine.calculate(subtotal)

        return {
            "subtotal": pricing["subtotal"],
            "tax": pricing["tax"],
            "shipping": pricing["shipping"],
            "discount": pricing["discount"],
            "total": pricing["total"],
            "item_count": item_count,
        }