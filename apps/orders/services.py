from django.db import transaction
from decimal import Decimal
from apps.cart.models import CartItem
from apps.products.models import ProductImage, ProductVariant
from .models import Order, OrderItem, OrderStatus, OrderStatusHistory




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


class OrderService:

    @staticmethod
    def _get_primary_image(product):
        primary = product.images.filter(is_primary=True).first()
        if primary:
            return primary.image_url

        first_image = product.images.first()
        if first_image:
            return first_image.image_url

        return ""
    




    @staticmethod
    @transaction.atomic
    def create_order(user, shipping_address, billing_address):

        cart_items = (
            CartItem.objects
            .select_related("variant", "variant__product")   # safe here (no FOR UPDATE)
            .filter(cart__user=user)
        )

        if not cart_items.exists():
            raise Exception("Cart is empty")

        subtotal = Decimal("0.00")
        order_items = []

        for item in cart_items:

            # 🔒 Lock only variant row
            variant = ProductVariant.objects.select_for_update().get(id=item.variant.id)

            inventory = variant.inventory
            product = variant.product

            if inventory.available_stock < item.quantity:
                raise Exception(f"{product.name} ({variant.size}) is out of stock")

            # Reserve stock
            inventory.reserved += item.quantity
            inventory.save(update_fields=["reserved"])

            unit_price = variant.price
            discount_percent = variant.discount_percent
            final_price = variant.selling_price

            total_price = final_price * item.quantity
            subtotal += total_price

            image_url = OrderService._get_primary_image(product)

            order_items.append({
                "product_id": product.id,
                "product_name": product.name,

                "variant_id": variant.id,
                "variant_size": variant.size,
                "variant_sku": variant.sku,

                "primary_image_url": image_url,

                "unit_price": unit_price,
                "discount_percent": discount_percent,
                "final_unit_price": final_price,

                "quantity": item.quantity,
                "total_price": total_price,
            })

        tax = Decimal("0.00")
        shipping = Decimal("0.00")
        discount = Decimal("0.00")

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

        for item in order_items:
            OrderItem.objects.create(order=order, **item)

        cart_items.delete()

        return order
    

    @staticmethod
    @transaction.atomic
    def cancel_order(order, user):

        if not order.can_cancel():
            raise Exception("Order cannot be cancelled")

        for item in order.items.select_for_update():
            variant = ProductVariant.objects.select_for_update().get(id=item.variant_id)
            inventory = variant.inventory

            # release reserved
            inventory.reserved -= item.quantity
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
    

    @staticmethod
    @transaction.atomic
    def update_status(order: Order, new_status: str, changed_by):

        if new_status not in ALLOWED_TRANSITIONS.get(order.status, []):
            raise ValueError(
                f"Invalid status transition from {order.status} to {new_status}"
            )

        old_status = order.status
        order.status = new_status
        order.save(update_fields=["status"])

        OrderStatusHistory.objects.create(
            order=order,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
        )

        return order