from django.db import transaction
from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from apps.cart.models import CartItem
from apps.products.models import ProductVariant
from .models import (
    Order,
    OrderItem,
    OrderStatus,
    OrderStatusHistory
)
from core.pricing import PricingEngine


# --------------------------------------------------------------------------
# STATUS TRANSITION RULES
# --------------------------------------------------------------------------

ALLOWED_TRANSITIONS = {
    "PENDING": ["CONFIRMED", "FAILED", "CANCELLED"],
    "CONFIRMED": ["PROCESSING", "CANCELLED"],
    "PROCESSING": ["SHIPPED"],
    "SHIPPED": ["DELIVERED"],
    "DELIVERED": [],
    "FAILED": [],
    "CANCELLED": [],
    "REFUNDED": [],
}


# --------------------------------------------------------------------------
# ORDER SERVICE
# --------------------------------------------------------------------------

class OrderService:

    # ----------------------------------------------------------------------
    # GET PRIMARY IMAGE
    # ----------------------------------------------------------------------

    @staticmethod
    def _get_primary_image(product):
        primary = product.images.filter(is_primary=True).first()
        if primary:
            return primary.image_url

        first_image = product.images.first()
        if first_image:
            return first_image.image_url

        return ""

    # ----------------------------------------------------------------------
    # CORE ENGINE (USED BY BOTH CART + BUY NOW)
    # ----------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def _create_order_from_items(user, items, shipping_address, billing_address):

        subtotal = Decimal("0.00")
        order_items_data = []

        for entry in items:
            variant = ProductVariant.objects.select_for_update().get(
                id=entry["variant"].id
            )

            inventory = variant.inventory
            product = variant.product
            quantity = entry["quantity"]

            if inventory.available_stock < quantity:
                raise ValidationError(
                    f"{product.name} ({variant.size}) is out of stock"
                )

            # Reserve stock
            inventory.reserved += quantity
            inventory.save(update_fields=["reserved"])

            unit_price = variant.price
            discount_percent = variant.discount_percent
            final_price = variant.selling_price

            total_price = final_price * quantity
            subtotal += total_price

            image_url = OrderService._get_primary_image(product)

            order_items_data.append({
                "product_id": product.id,
                "product_name": product.name,

                "variant_id": variant.id,
                "variant_size": variant.size,
                "variant_sku": variant.sku,

                "primary_image_url": image_url,

                "unit_price": unit_price,
                "discount_percent": discount_percent,
                "final_unit_price": final_price,

                "quantity": quantity,
                "total_price": total_price,
            })

        pricing = PricingEngine.calculate(subtotal)

        tax = pricing["tax"]
        shipping = pricing["shipping"]
        discount = pricing["discount"]
        total = pricing["total"]

        total = subtotal + tax + shipping - discount

        total = subtotal + tax + shipping - discount

        order = Order.objects.create(
            user=user,
            subtotal_amount=subtotal,
            tax_amount=tax,
            shipping_amount=shipping,
            discount_amount=discount,
            total_amount=total,
            shipping_address=shipping_address,
            billing_address=billing_address,
            status=OrderStatus.PENDING
        )

        for item in order_items_data:
            OrderItem.objects.create(order=order, **item)

        return order

    # ----------------------------------------------------------------------
    # CART CHECKOUT
    # ----------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def create_order(user, shipping_address, billing_address):

        cart_items = (
            CartItem.objects
            .select_related("variant", "variant__product")
            .filter(cart__user=user)
        )

        if not cart_items.exists():
            raise ValidationError("Cart is empty")

        items = [
            {
                "variant": item.variant,
                "quantity": item.quantity
            }
            for item in cart_items
        ]

        order = OrderService._create_order_from_items(
            user=user,
            items=items,
            shipping_address=shipping_address,
            billing_address=billing_address
        )

        # Clear cart after order creation
        cart_items.delete()

        return order

    # ----------------------------------------------------------------------
    # BUY NOW (SINGLE PRODUCT CHECKOUT)
    # ----------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def create_single_product_order(
        user,
        variant_id,
        quantity,
        shipping_address,
        billing_address
    ):

        variant = get_object_or_404(
            ProductVariant.objects.select_related("product"),
            id=variant_id
        )

        items = [{
            "variant": variant,
            "quantity": quantity
        }]

        return OrderService._create_order_from_items(
            user=user,
            items=items,
            shipping_address=shipping_address,
            billing_address=billing_address
        )

    # ----------------------------------------------------------------------
    # CANCEL ORDER
    # ----------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def cancel_order(order, user):

        if not order.can_cancel():
            raise ValidationError("Order cannot be cancelled")

        for item in order.items.select_for_update():
            variant = ProductVariant.objects.select_for_update().get(
                id=item.variant_id
            )

            inventory = variant.inventory

            # Release reserved stock safely
            inventory.reserved = max(
                0,
                inventory.reserved - item.quantity
            )
            inventory.save(update_fields=["reserved"])

        old_status = order.status
        order.status = OrderStatus.CANCELLED
        order.save(update_fields=["status"])

        OrderStatusHistory.objects.create(
            order=order,
            old_status=old_status,
            new_status=OrderStatus.CANCELLED,
            changed_by=user
        )

        return order

    # ----------------------------------------------------------------------
    # UPDATE ORDER STATUS (ADMIN / SYSTEM)
    # ----------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def update_status(order: Order, new_status: str, changed_by):

        if new_status not in ALLOWED_TRANSITIONS.get(order.status, []):
            raise ValidationError(
                f"Invalid status transition from {order.status} to {new_status}"
            )

        old_status = order.status
        order.status = new_status
        order.save(update_fields=["status"])

        OrderStatusHistory.objects.create(
            order=order,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by
        )

        return order
    


