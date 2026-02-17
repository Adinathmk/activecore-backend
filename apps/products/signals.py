from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProductVariant, Inventory

@receiver(post_save, sender=ProductVariant)
def create_inventory_for_variant(sender, instance, created, **kwargs):
    if created:
        Inventory.objects.create(variant=instance)
