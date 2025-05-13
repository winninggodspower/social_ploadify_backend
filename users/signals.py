from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from social_accounts.models import Brand

@receiver(post_save, sender=User)
def create_default_brand(sender, instance, created, **kwargs):
    if created:
        brand_name = instance.handle if instance.handle else f"{instance.first_name} {instance.last_name}'s Brand"

        Brand.objects.create(
            user=instance,
            name=brand_name,
            is_default=True
        )
