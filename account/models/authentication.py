
from rest_framework.authtoken.models import Token


from django.utils import timezone
from django.utils.translation import gettext_lazy as _

AUTH_TOKEN_EXPIRY_DAYS = 30
# AUTH_TOKEN_EXPIRY_DAYS = settings.AUTH_TOKEN_EXPIRY_DAYS or 30


class TokenAuthenticationProxyModel(Token):
    """ Token Authentication Proxy Model"""
    class Meta:
        proxy = True

    def has_expired(self):
        """ Check if token has expired

            Returns:
                bool: True if token has expired, False otherwise
        """
        return self.created < timezone.now(
        ) - timezone.timedelta(days=AUTH_TOKEN_EXPIRY_DAYS)

    def has_almost_expired(self):
        """ Check if token has almost expired

            Returns:
                bool: True if token has almost expired, False otherwise
        """
        return self.created < timezone.now(
        ) - timezone.timedelta(days=AUTH_TOKEN_EXPIRY_DAYS - 1)
