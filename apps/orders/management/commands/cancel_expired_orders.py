from django.core.management.base import BaseCommand
from apps.orders.services import OrderService


class Command(BaseCommand):
    help = "Cancel expired unpaid orders"

    def handle(self, *args, **kwargs):

        OrderService.cancel_expired_orders()

        self.stdout.write(
            self.style.SUCCESS("Expired orders cancelled successfully")
        )