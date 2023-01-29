from django.db.models.signals import post_save
from account.models import User
from django.dispatch import receiver
from wallet.models import WalletModel


@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        WalletModel.objects.create(user=instance)
