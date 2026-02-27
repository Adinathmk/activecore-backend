from decimal import Decimal
from django.conf import settings


class PricingEngine:

    GST_RATE = Decimal("0.18")  

    @staticmethod
    def calculate(subtotal: Decimal):
        tax = (subtotal * PricingEngine.GST_RATE).quantize(Decimal("0.01"))
        shipping = Decimal("0.00")
        discount = Decimal("0.00")

        total = subtotal + tax + shipping - discount

        return {
            "subtotal": subtotal,
            "tax": tax,
            "shipping": shipping,
            "discount": discount,
            "total": total,
        }