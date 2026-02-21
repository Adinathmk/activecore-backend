import uuid
from django.db import models
from django.conf import settings


class OrderStatus(models.TextChoices):
    PENDING = "PENDING", "Pending Payment"
    CONFIRMED = "CONFIRMED", "Confirmed"
    PROCESSING = "PROCESSING", "Processing"
    SHIPPED = "SHIPPED", "Shipped"
    DELIVERED = "DELIVERED", "Delivered"
    CANCELLED = "CANCELLED", "Cancelled"
    FAILED = "FAILED", "Payment Failed"
    REFUNDED = "REFUNDED", "Refunded"


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders"
    )

    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        db_index=True
    )

    subtotal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    currency = models.CharField(max_length=10, default="INR")

    shipping_address = models.JSONField()
    billing_address = models.JSONField()

    payment_reference = models.CharField(max_length=255, blank=True, null=True)

    placed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def can_cancel(self):
        return self.status in ["PENDING", "CONFIRMED"]

    def __str__(self):
        return f"Order {self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )

    # 🔹 Product Snapshot
    product_id = models.UUIDField()
    product_name = models.CharField(max_length=255)

    # 🔹 Variant Snapshot (VERY IMPORTANT)
    variant_id = models.UUIDField()
    variant_size = models.CharField(max_length=10)
    variant_sku = models.CharField(max_length=100)

    # 🔹 Image Snapshot
    primary_image_url = models.URLField()

    # 🔹 Pricing Snapshot
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    final_unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_history"
    )

    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL
    )
    changed_at = models.DateTimeField(auto_now_add=True)