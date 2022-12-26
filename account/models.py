# import token model from django rest framework
from rest_framework.authtoken.models import Token
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db import models
import random
import hashlib
import string

TOKEN_EXPIRY_HOURS: int = getattr(settings, 'TOKEN_EXPIRY_HOURS', 1)


class TokenProxyModel(Token):
    """ Token Authentication Proxy Model"""
    class Meta:
        proxy = True

    def has_expired(self):
        return self.created < timezone.now(
        ) - timezone.timedelta(hours=TOKEN_EXPIRY_HOURS)

    def has_almost_expired(self):
        return self.created < timezone.now(
        ) - timezone.timedelta(hours=TOKEN_EXPIRY_HOURS - 1)


class TokenVerificationModel(models.Model):
    """ Token Verification Model
    """
    token = models.CharField(max_length=255, verbose_name=_('Token'))
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Created'))

    class Meta:
        abstract = True

    def __str__(self):
        return self.token

    def has_expired(self):
        return self.created < timezone.now(
        ) - timezone.timedelta(hours=TOKEN_EXPIRY_HOURS)

    @classmethod
    def generate_token(cls):
        """ Generate a 6 digit tokem
        """
        token = ''.join(random.choices(string.digits, k=6))
        return token

    def get_hash(self, _token):
        """ Hash the token using SHA256 """
        return hashlib.sha256(_token.encode('utf-8')).hexdigest()

    def is_valid(self, _token):
        """ Compare the hashed token with the one in
            the database and check if it has expired

            Args:
                _token (str): The token to verify

            Returns:
                bool: True if the token is valid, False otherwise
         """
        if self.token == self.get_hash(_token):
            if not self.has_expired():
                return True
        return False

    def save(self, *args, **kwargs):
        """ Hash the token before saving """
        self.token = self.get_hash(self.token)
        super().save(*args, **kwargs)


class EmailTokenVerificationModel(TokenVerificationModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('User'),
        related_name='email_token_verification'
    )

    class Meta:
        verbose_name = _('Email verification token')
        verbose_name_plural = _('Email  verification tokens')


class ResetPasswordVerificationModel(TokenVerificationModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('User'),
        related_name='reset_password_token_verification'
    )

    class Meta:
        verbose_name = _('Reset password token')
        verbose_name_plural = _('Reset password tokens')
