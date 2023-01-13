from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from account.models import User
from account.modules.authentication.social.google import GoogleProvider
from unittest.mock import patch
from core.exceptions import AuthorizationError


class SocialSignInAPITestCase(TestCase):
    def setUp(self):
        # Set up a user to test with
        self.user_data = {
            "google_id": "12345",
            "email": "test@example.com",
            "is_active": True,
            "first_name": "John",
            "last_name": "Doe",
        }
        self.user = User(**self.user_data)
        self.user.save()
        self.url = reverse('account:account-social-signin')

    def test_post_existing_user(self):
        # Test logging in with an existing user
        with patch.object(GoogleProvider, 'login', return_value=(self.user, False)):
            response = self.client.post(
                self.url, HTTP_AUTHORIZATION='Google abc123')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, self.user.login())  # type: ignore

    def test_post_new_user(self):
        # Test signing up with a new user
        with patch.object(GoogleProvider, 'login', return_value=(self.user, True)):
            response = self.client.post(
                self.url, HTTP_AUTHORIZATION='Google abc123')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data, self.user.login())  # type: ignore

    def test_post_invalid_token(self):
        # Test signing in with an invalid token
        with patch.object(GoogleProvider, 'login', side_effect=AuthorizationError):
            response = self.client.post(
                self.url, HTTP_AUTHORIZATION='Bearer abc123')
            self.assertEqual(response.status_code,
                             status.HTTP_401_UNAUTHORIZED)

    def test_post_missing_token(self):
        # Test signing in without a token
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
