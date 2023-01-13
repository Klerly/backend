from datetime import timedelta
from django.utils import timezone
from account.models.authentication import TokenAuthenticationProxyModel
from django.test import TestCase
from django.conf import settings
from django.contrib.auth import get_user_model


class TokenAuthenticationProxyModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(  # type: ignore
            email="test@email.com",
            username="test",
        )
        self.token = TokenAuthenticationProxyModel.objects.create(
            key='123',
            user=self.user
        )

    def test_has_expired(self):
        self.token.created = timezone.now() - timedelta(days=settings.AUTH_TOKEN_EXPIRY_DAYS)
        self.token.save()
        assert self.token.has_expired() == True

    def test_has_not_expired(self):
        self.token.created = timezone.now() - timedelta(days=settings.AUTH_TOKEN_EXPIRY_DAYS - 1)
        self.token.save()
        assert self.token.has_expired() == False

    def test_has_almost_expired(self):
        self.token.created = timezone.now() - timedelta(days=settings.AUTH_TOKEN_EXPIRY_DAYS - 1)
        self.token.save()
        assert self.token.has_almost_expired() == True

    def test_has_not_almost_expired(self):
        self.token.created = timezone.now() - timedelta(days=settings.AUTH_TOKEN_EXPIRY_DAYS - 2)
        self.token.save()
        assert self.token.has_almost_expired() == False
