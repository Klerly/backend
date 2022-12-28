from django.test import TestCase
from core.exceptions import HttpValidationError
from account.modules.authentication.social.google import GoogleProvider
from account.modules.authentication.social.base import SocialProvider
from unittest import mock


class SocialProviderTestCase(TestCase):
    def test_init(self):
        # Test that the provider is correctly initialized
        # with the correct token
        provider = SocialProvider('Google abc123')
        self.assertIsInstance(provider.provider, GoogleProvider)
        self.assertEqual(provider.provider.token, 'abc123')

        # Test that an HttpValidationError is raised
        # if the authorization header is missing
        with self.assertRaises(HttpValidationError):
            SocialProvider('')

        # Test that an HttpValidationError is raised
        # if the authorization header is invalid
        with self.assertRaises(HttpValidationError):
            SocialProvider('Google')

        # Test that an HttpValidationError is raised
        # if the provider is unsupported
        with self.assertRaises(HttpValidationError):
            SocialProvider('Facebook abc123')

    def test_login(self):
        # Test that the login method of the provider is called
        # when the login method of the SocialProvider is called
        provider = SocialProvider('Google abc123')
        provider.provider.login = mock.Mock()
        provider.login()
        provider.provider.login.assert_called_once()
