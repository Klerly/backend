from django.test import TestCase
from account.modules.authentication import CustomTokenAuthentication
from account.models.authentication import TokenAuthenticationProxyModel
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import exceptions
from django.conf import settings

User = get_user_model()


class CustomTokenAuthenticationTestCase(TestCase):
    def test_authenticate_credentials_success(self):
        # Create a user and a valid token for the user
        user = User.objects.create(username='testuser', password='testpass')
        token = TokenAuthenticationProxyModel.objects.create(user=user)

        # Test that the method returns a tuple containing the user and token
        auth = CustomTokenAuthentication()
        user, token = auth.authenticate_credentials(token.key)
        self.assertEqual(user, user)
        self.assertEqual(token, token)

    def test_authenticate_credentials_invalid_token(self):
        # Test that the method raises an AuthenticationFailed exception when the token is invalid
        auth = CustomTokenAuthentication()
        with self.assertRaises(exceptions.AuthenticationFailed):
            auth.authenticate_credentials('invalid')

    def test_authenticate_credentials_inactive_user(self):
        # Create a user and a valid token for the user
        user = User.objects.create(
            username='testuser', password='testpass', is_active=False)
        token = TokenAuthenticationProxyModel.objects.create(user=user)

        # Test that the method raises an AuthenticationFailed exception when the user is inactive or deleted
        # and check the message

        auth = CustomTokenAuthentication()
        with self.assertRaises(exceptions.AuthenticationFailed) as cm:
            auth.authenticate_credentials(token.key)
            self.assertEqual(
                cm.exception.detail, 'User inactive or deleted.')

    def test_authenticate_credentials_expired_token(self):
        # Create a user and an expired token for the user
        user = User.objects.create(username='testuser', password='testpass')
        token = TokenAuthenticationProxyModel.objects.create(
            user=user
        )
        token.created = timezone.now(
        ) - timezone.timedelta(days=settings.AUTH_TOKEN_EXPIRY_DAYS + 1)
        token.save()

        # Test that the method raises an AuthenticationFailed exception when the token has expired
        auth = CustomTokenAuthentication()
        with self.assertRaises(exceptions.AuthenticationFailed) as cm:
            auth.authenticate_credentials(token.key)
            self.assertEqual(cm.exception.detail, 'Token has expired')
