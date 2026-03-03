from django.db import transaction
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import ValidationError

from apps.cart.models import CartItem
from apps.products.models import ProductVariant
from .models import (
    Order,
    OrderItem,
    OrderStatus,
    OrderStatusHistory,
    Payment,
    PaymentStatus,
    PaymentMethod,
)

from core.pricing import PricingEngine

import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


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
    def _create_order_from_items(user, items, shipping_address, billing_address,payment_method):

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

            # 🔥 Reserve stock
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

        total = subtotal + tax + shipping - discount

        # 🔥 Create order
        order = Order.objects.create(
            user=user,
            subtotal_amount=subtotal,
            tax_amount=tax,
            shipping_amount=shipping,
            discount_amount=discount,
            total_amount=total,
            shipping_address=shipping_address,
            billing_address=billing_address,
            status=OrderStatus.PENDING,
            expires_at=timezone.now() + timedelta(minutes=10),
            payment_method=payment_method,
            is_paid=False,
        )

        # ✅ COD LOGIC
        if payment_method == PaymentMethod.COD:
            order.status = OrderStatus.CONFIRMED
            order.is_paid = False
            order.expires_at = None  # COD should not expire
            order.save(update_fields=["status", "is_paid", "expires_at"])

        for item in order_items_data:
            OrderItem.objects.create(order=order, **item)

        return order

    # ----------------------------------------------------------------------
    # CART CHECKOUT
    # ----------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def create_order(user, shipping_address, billing_address, payment_method):

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
            billing_address=billing_address,
            payment_method=payment_method
        )

        cart_items.delete()
        return order

    # ----------------------------------------------------------------------
    # BUY NOW
    # ----------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def create_single_product_order(
        user,
        variant_id,
        quantity,
        shipping_address,
        billing_address,
        payment_method
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
            billing_address=billing_address,
            payment_method=payment_method            
        )
    

    # ----------------------------------------------------------------------
    # CANCEL ORDER (MANUAL)
    # ----------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def cancel_order(order, user):

        if not order.can_cancel():
            raise ValidationError("Order cannot be cancelled")

        OrderService._release_inventory(order)

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
    # RELEASE INVENTORY (REUSABLE)
    # ----------------------------------------------------------------------

    @staticmethod
    def _release_inventory(order):
        for item in order.items.select_for_update():
            variant = ProductVariant.objects.select_for_update().get(
                id=item.variant_id
            )

            inventory = variant.inventory
            inventory.reserved = max(0, inventory.reserved - item.quantity)
            inventory.save(update_fields=["reserved"])

    # ----------------------------------------------------------------------
    # AUTO CANCEL EXPIRED ORDERS
    # ----------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def cancel_expired_orders():

        now = timezone.now()

        expired_orders = (
            Order.objects
            .select_related("payment")
            .prefetch_related("items")
            .filter(
                status=OrderStatus.PENDING,
                expires_at__lt=now,
                is_paid=False
            )
        )

        for order in expired_orders:

            # Cancel Stripe PaymentIntent (only for ONLINE)
            if order.payment_method == PaymentMethod.ONLINE and hasattr(order, "payment"):
                try:
                    stripe.PaymentIntent.cancel(
                        order.payment.stripe_payment_intent_id
                    )

                    order.payment.status = PaymentStatus.FAILED
                    order.payment.save(update_fields=["status"])

                except Exception:
                    pass

            OrderService._release_inventory(order)

            order.status = OrderStatus.CANCELLED
            order.is_paid = False
            order.save(update_fields=["status", "is_paid"])


# --------------------------------------------------------------------------
# STRIPE SERVICE
# --------------------------------------------------------------------------

class StripeService:

    @staticmethod
    def create_payment_intent(order):

        # ❌ COD protection
        if order.payment_method == PaymentMethod.COD:
            raise ValidationError("COD orders do not require online payment.")

        # ❌ Expired protection
        if order.is_expired():
            raise ValidationError("Order has expired.")

        if order.status != OrderStatus.PENDING:
            raise ValidationError("Order is not eligible for payment.")

        existing_payment = getattr(order, "payment", None)

        if existing_payment:
            return stripe.PaymentIntent.retrieve(
                existing_payment.stripe_payment_intent_id
            )

        amount_in_paise = int(order.total_amount * 100)

        intent = stripe.PaymentIntent.create(
            amount=amount_in_paise,
            currency=order.currency.lower(),
            metadata={
                "order_id": str(order.id),
                "user_id": str(order.user.id),
            },
            idempotency_key=f"order_{order.id}"
        )

        Payment.objects.create(
            order=order,
            stripe_payment_intent_id=intent.id,
            amount=amount_in_paise,
            currency=order.currency,
            status=PaymentStatus.CREATED,
            raw_response=intent
        )

        order.payment_reference = intent.id
        order.save(update_fields=["payment_reference"])

        return intent

    # ----------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def handle_payment_success(payment_intent):

        metadata = payment_intent.get("metadata", {})
        order_id = metadata.get("order_id")

        if not order_id:
            return

        order = Order.objects.select_for_update().get(id=order_id)

        # If already processed → ignore
        if order.status == OrderStatus.CONFIRMED:
            return

        # If expired → ignore success
        if order.is_expired():
            return

        order.status = OrderStatus.CONFIRMED
        order.is_paid = True
        order.expires_at = None
        order.save(update_fields=["status", "is_paid", "expires_at"])

        payment = Payment.objects.get(
            stripe_payment_intent_id=payment_intent["id"]
        )
        payment.status = PaymentStatus.SUCCEEDED
        payment.save(update_fields=["status"])

    # ----------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def handle_payment_failed(payment_intent):

        metadata = payment_intent.get("metadata", {})
        order_id = metadata.get("order_id")

        if not order_id:
            return
        
        if order.status != OrderStatus.PENDING:
            return

        order = Order.objects.select_for_update().get(id=order_id)

        # If already processed → ignore
        
        # Only allow failure if still pending
        if order.status != OrderStatus.PENDING:
            return

        OrderService._release_inventory(order)

        order.status = OrderStatus.FAILED
        order.is_paid = False
        order.save(update_fields=["status", "is_paid"])

        payment = Payment.objects.get(
            stripe_payment_intent_id=payment_intent["id"]
        )
        payment.status = PaymentStatus.FAILED
        payment.save(update_fields=["status"])