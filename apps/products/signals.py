from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProductVariant, Inventory
import cloudinary.uploader
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import ProductImage

@receiver(post_save, sender=ProductVariant)
def create_inventory_for_variant(sender, instance, created, **kwargs):
    if created:
        Inventory.objects.create(variant=instance)




@receiver(pre_delete, sender=ProductImage)
def delete_cloudinary_image(sender, instance, **kwargs):
    if instance.image:
        cloudinary.uploader.destroy(instance.image.public_id)