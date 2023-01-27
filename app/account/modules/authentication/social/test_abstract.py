from django.test import TestCase
from account.modules.authentication.social.abstract import AbstractSocialProvider
from unittest import mock
import datetime as dt
from account.models import User


class AbstractSocialProviderTestCase(TestCase):
    def test_check_expiry(self):
        # Test that the function returns True when the tokens have expired
        iat = int(dt.datetime.utcnow().timestamp())
        iat -= 120

        with self.settings(OAUTH_TOKEN_TTL_MINS=1):
            self.assertTrue(AbstractSocialProvider._check_expiry(iat))

        # Test that the function returns False when the tokens have not expired
        with self.settings(OAUTH_TOKEN_TTL_MINS=5):
            self.assertFalse(
                AbstractSocialProvider._check_expiry(iat))

    def test_unimplemented_abstract_methods(self):
        # Test that a TypeError is raised when the method is called
        with self.assertRaises(TypeError) as context:
            class BadSocialProvider(AbstractSocialProvider):
                pass
            BadSocialProvider()  # type: ignore
            self.assertTrue(
                '_get_or_create_user' in str(context.exception)
            )
            self.assertTrue(
                '_validate_token' in str(context.exception)
            )

    def test_login(self):
        # Test that the login method returns the expected user and created flag
        user = User(email='test@example.com')

        class TestSocialProvider(AbstractSocialProvider):
            def _validate_token(self):
                pass

            def _get_or_create_user(self, user):
                pass
        provider = TestSocialProvider()

        # Mock the _validate_token and _get_or_create_user methods to return the user and created flag
        provider._validate_token = mock.Mock(return_value=user)
        provider._get_or_create_user = mock.Mock(return_value=(user, True))
        returned_user, created = provider.login()

        self.assertEqual(returned_user, user)
        self.assertTrue(created)
        provider._validate_token.assert_called_once()
        provider._get_or_create_user.assert_called_once_with(user)
