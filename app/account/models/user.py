
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from account.models.authentication import TokenAuthenticationProxyModel
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from core.models import BaseModel
from django.conf import settings
from decimal import Decimal


class User(AbstractUser):
    """ User Model """
    google_id = models.CharField(
        max_length=255,
        blank=True, null=True,
        verbose_name=_('Google ID')
    )

    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Is Verified')
    )

    email = models.EmailField(
        unique=True,
        verbose_name=_('Email')
    )

    def verify(self):
        """ verify a user """
        self.is_verified = True
        self.save()
        return

    def login(self):
        """ Login user and return token 

            Returns:
                dict: {
                    'token': str, 
                    'is_verified': bool
                }
        """
        try:
            token = TokenAuthenticationProxyModel.objects.get(user=self)
            if token.has_almost_expired() or token.has_expired():
                token.delete()
                token = TokenAuthenticationProxyModel.objects.create(user=self)
        except ObjectDoesNotExist:
            token = TokenAuthenticationProxyModel.objects.create(user=self)

        self.last_login = timezone.now()
        self.save()
        return {
            "token": token.key,
            "is_verified": self.is_verified,
        }

    def logout(self):
        """ Logout user """
        try:
            self.auth_token.delete()  # type: ignore
        except ObjectDoesNotExist:
            pass
        return


class Seller(BaseModel):
    """ Seller Model """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('Seller Profile'),
        related_name='seller_profile',
    )

    handle = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('Handle')
    )

    name = models.CharField(
        max_length=255,
        verbose_name=_('Name')
    )
    about = models.TextField(
        blank=True, null=True,
        verbose_name=_('About')
    )

    """ Seller's finalised earnings """
    earnings = models.DecimalField(
        max_digits=10, decimal_places=10,
        default=Decimal(0.00),
        verbose_name=_('Earnings')
    )
    """ Seller's pending earnings """
    pending_earnings = models.DecimalField(
        max_digits=10, decimal_places=10,
        default=Decimal(0.00),
        verbose_name=_('Pending Earnings')
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Seller')
        verbose_name_plural = _('Sellers')
