from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from account.models.verification import (
    TokenVerificationModel,
    EmailTokenVerificationModel
)
import string
import hashlib
from django.utils import timezone
from django.utils.timezone import timedelta

from django.conf import settings


class DummyTokenVerificationModel(EmailTokenVerificationModel):
    class Meta:
        proxy = True


class TokenVerificationModelTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(  # type: ignore
            email="test@email.com",
            username="test",
        )
        self.user2 = get_user_model().objects.create_user(  # type: ignore
            email="test2@email.com",
            username="test2",
        )
        self.user3 = get_user_model().objects.create_user(  # type: ignore
            email="test3@email.com",
            username="test3",
        )

        self.verification_token = DummyTokenVerificationModel.objects.create(
            user=self.user)
        self.verification_token.token = '123456'
        self.verification_token.save()

    def test_generate_token(self):
        # Ensure the generate_token method generates a 6-digit token
        token = TokenVerificationModel.generate_token()
        self.assertEqual(len(token), 6)
        self.assertTrue(all(c in string.digits for c in token))

    def test_get_hash(self):
        # Ensure the get_hash method hashes the token correctly
        salt = settings.SECRET_KEY
        expected_hash = hashlib.sha256(
            ('123456' + salt).encode('utf-8')).hexdigest()
        self.assertEqual(self.verification_token.get_hash(
            '123456'), expected_hash)

    def test_is_valid(self):
        # Ensure the is_valid method returns True for a valid token
        self.assertTrue(self.verification_token.is_valid('123456'))

        # Ensure the is_valid method returns False for an invalid token
        self.assertFalse(self.verification_token.is_valid('654321'))

    def test_has_expired_true(self):
        token = DummyTokenVerificationModel.objects.create(
            user=self.user2
        )
        token.created = timezone.now(
        ) - timedelta(hours=settings.VERIFICATION_TOKEN_EXPIRY_HOURS + 1)
        token.save()
        self.assertTrue(token._has_expired())

    def test_has_expired_false(self):
        token = DummyTokenVerificationModel.objects.create(
            user=self.user3
        )
        self.assertFalse(token._has_expired())
