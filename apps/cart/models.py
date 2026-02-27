from django.db import models
from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db.models import F
from core.pricing import PricingEngine



class Cart(models.Model):
    """
    One active cart per user.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="cart",
        on_delete=models.CASCADE
    )

    is_active = models.BooleanField(default=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    shipping_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"Cart - {self.user.email}"

    def recalculate_totals(self):
        items = self.items.all()

        subtotal = sum(item.total_price for item in items)

        pricing = PricingEngine.calculate(subtotal)

        self.subtotal = pricing["subtotal"]
        self.tax_amount = pricing["tax"]
        self.shipping_amount = pricing["shipping"]
        self.total_amount = pricing["total"]

        self.save(update_fields=[
            "subtotal",
            "tax_amount",
            "shipping_amount",
            "total_amount",
            "updated_at"
        ])


from apps.products.models import ProductVariant



class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        related_name="items",
        on_delete=models.CASCADE
    )

    variant = models.ForeignKey(
        ProductVariant,
        related_name="cart_items",
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    # 🔥 Snapshot Fields
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("cart", "variant")
        indexes = [
            models.Index(fields=["cart"]),
            models.Index(fields=["variant"]),
        ]

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.variant} x {self.quantity}"