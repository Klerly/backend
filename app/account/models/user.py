
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from account.models.authentication import TokenAuthenticationProxyModel
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone


class User(AbstractUser):
    """ User Model """
    google_id = models.CharField(
        max_length=255,
        blank=True, null=True,
        verbose_name=_('Google ID')
    )

    def activate(self):
        """ Activate user """
        self.is_active = True
        self.save()
        return

    def login(self):
        """ Login user and return token 

            Returns:
                dict: {
                    'token': str, 
                    'is_active': bool
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
            "is_active": self.is_active
        }

    def logout(self):
        """ Logout user """
        try:
            self.auth_token.delete()  # type: ignore
        except ObjectDoesNotExist:
            pass
        return
