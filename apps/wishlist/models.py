from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint


class Wishlist(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist"
    )
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} Wishlist"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product_variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.PROTECT,
        related_name="wishlist_items"
    )

    price_at_added = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    is_active = models.BooleanField(default=True)

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["wishlist", "product_variant"],
                name="unique_wishlist_item"
            )
        ]
        indexes = [
            models.Index(fields=["wishlist", "product_variant"]),
        ]

    def __str__(self):
        return f"{self.product_variant} in wishlist"