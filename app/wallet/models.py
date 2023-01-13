from django.db import models
from core.models import BaseModel
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from account.models import User
from typing import Dict, Any


class WalletModel(BaseModel):
    user: User = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('User'),
        related_name='wallet'
    )  # type: ignore
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal(0.00)
    )  # may be less than 0

    def __str__(self):
        return f"{self.user.username}'s Wallet"

    class Meta:
        verbose_name = _('Wallet')
        verbose_name_plural = _('Wallets')

    def fund(self, amount: int):
        from wallet.modules.payment import Payment

        self.balance += Payment.validate_integer_amount(amount)
        self.save()

    def deduct(self, amount: Decimal):
        from wallet.modules.payment import Payment

        self.balance -= Payment.validate_decimal_amount(amount)
        self.save()


class TransactionModel(BaseModel):
    class Type(models.TextChoices):
        DEPOSIT = 'DEP', _('Deposit')

    class Status(models.TextChoices):
        SUCCESS = 'SUC', _('Success')
        PENDING = 'PEN', _('Pending')
        FAILED = 'FAL', _('Failed')

    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')

    reference = models.CharField(
        max_length=255,
        verbose_name=_('Reference'),
        primary_key=True
    )

    user: User = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('User'),
        related_name='transactions'
    )  # type: ignore

    amount = models.IntegerField(
        verbose_name=_('Amount')
    )

    type = models.CharField(
        max_length=3,
        choices=Type.choices,
        verbose_name=_('Type'),
        default=Type.DEPOSIT
    )

    status = models.CharField(
        max_length=3,
        choices=Status.choices,
        verbose_name=_('Status'),
        default=Status.PENDING
    )

    def __str__(self):
        return f"{self.user.username}'s {self.type} Transaction"


class CardModel(BaseModel):
    class Meta:
        verbose_name = _('Card')
        verbose_name_plural = _('Cards')

    user: User = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('User'),
        related_name='cards'
    )  # type: ignore

    keep = models.BooleanField(
        default=False,
        verbose_name=_('Keep')
    )

    type = models.CharField(
        max_length=255,
        verbose_name=_('Type')
    )
    last_four = models.CharField(
        max_length=4,
        verbose_name=_('Last Four')
    )
    exp_month = models.CharField(
        max_length=2,
        verbose_name=_('Expiration Month')
    )
    exp_year = models.CharField(
        max_length=4,
        verbose_name=_('Expiration Year')
    )

    authorization_code = models.CharField(
        max_length=255,
        verbose_name=_('Authorization Code')
    )
    signature = models.CharField(
        max_length=255,
        verbose_name=_('Signature')
    )

    # paystack json field
    data: Dict[str, Any] = models.JSONField(
        verbose_name=_('Paystack data'),
        null=True,
        blank=True
    )  # type: ignore

    def __str__(self):
        return f"{self.user.username}'s Card"

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.last_four = self.data['last4']
            self.exp_month = self.data['exp_month']
            self.exp_year = self.data['exp_year']
            self.authorization_code = self.data['authorization_code']
            self.signature = self.data['signature']
        super().save(*args, **kwargs)
