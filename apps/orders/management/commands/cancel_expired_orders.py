from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.conf import settings
import stripe

from apps.orders.models import Order, OrderStatus
from apps.products.models import ProductVariant

stripe.api_key = settings.STRIPE_SECRET_KEY


class Command(BaseCommand):
    help = "Cancel expired unpaid orders"

    def handle(self, *args, **kwargs):

        now = timezone.now()

        expired_orders = (
            Order.objects
            .select_related("payment")
            .prefetch_related("items")
            .filter(
                status=OrderStatus.PENDING,
                expires_at__lt=now
            )
        )

        cancelled_count = 0

        for order in expired_orders:

            with transaction.atomic():

                # Cancel Stripe PaymentIntent
                if hasattr(order, "payment"):
                    try:
                        stripe.PaymentIntent.cancel(
                            order.payment.stripe_payment_intent_id
                        )
                    except Exception:
                        pass

                # Release inventory
                for item in order.items.select_for_update():
                    variant = ProductVariant.objects.select_for_update().get(
                        id=item.variant_id
                    )

                    inventory = variant.inventory

                    inventory.reserved = max(
                        0,
                        inventory.reserved - item.quantity
                    )
                    inventory.save(update_fields=["reserved"])

                order.status = OrderStatus.CANCELLED
                order.save(update_fields=["status"])

                cancelled_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Cancelled {cancelled_count} expired orders"
            )
        )