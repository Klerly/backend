from django.test import TestCase
from core.exceptions import AuthorizationError
from unittest import mock
import json
from account.modules.authentication.social.google import GoogleProvider
from django.contrib.auth import get_user_model
from account.models import User


class GoogleProviderTestCase(TestCase):
    def setUp(self):
        # Set up a mock response for the requests.post call
        # in the _get_id_token method
        self.mock_response = mock.Mock()
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = {'id_token': '12345'}
        self.patch_requests_post = mock.patch(
            'account.modules.authentication.social.google.requests.post',
            return_value=self.mock_response
        )
        self.patch_requests_post.start()
        self.user_data = {
            "google_id": "google-id-12345",
            "username": "test@example.com",
            "email": "test@example.com",
            "is_active": True,
            "first_name": "John",
            "last_name": "Doe",
        }

    def tearDown(self):
        self.patch_requests_post.stop()

    def test_get_id_token(self):
        # Test that the _get_id_token method returns the id_token
        # from the mock response
        provider = GoogleProvider('abc123')
        id_token = provider._get_id_token()
        self.assertEqual(id_token, '12345')

        # Test that an AuthorizationError is raised
        # if the response status code is not 200
        self.mock_response.status_code = 401
        with self.assertRaises(AuthorizationError):
            provider._get_id_token()

    def test_get_or_create_user_sets_google_id(self):
        # Test that the method sets the google_id if it is not set
        self.user_data["google_id"] = None
        user = User.objects.create_user(**self.user_data)  # type: ignore

        provider = GoogleProvider('abc123')
        google_id = 'google-id-12345'
        user.google_id = google_id
        returned_user, created = provider._get_or_create_user(user)
        self.assertFalse(created)
        self.assertEqual(returned_user.google_id, google_id)

    def test_get_or_create_user_activates_inactive_accounts(self):
        # Test that inactive accounts are activated
        self.user_data["is_active"] = False
        user = User.objects.create_user(**self.user_data)  # type: ignore

        provider = GoogleProvider('abc123')
        returned_user, created = provider._get_or_create_user(user)
        self.assertFalse(created)
        self.assertTrue(returned_user.is_active)

    def test_get_or_create_user_returns_new_user(self):
        # Test that the method returns a new user
        # and sets the google_id
        user = User(**self.user_data)

        provider = GoogleProvider('abc123')
        returned_user, created = provider._get_or_create_user(user)
        self.assertNotEqual(returned_user, user)
        self.assertTrue(created)
        self.assertEqual(returned_user.google_id, self.user_data["google_id"])
        self.assertEqual(returned_user.email, self.user_data["email"])
        self.assertTrue(returned_user.is_active)
        self.assertEqual(returned_user.first_name,
                         self.user_data["first_name"])
        self.assertEqual(returned_user.last_name, self.user_data["last_name"])

    def test_get_or_create_user_raises_http_validation_error(self):
        # Test that an AuthorizationError is raised
        # if the google_id of the existing user is different
        # from the google_id of the provided user

        User.objects.create_user(**self.user_data)  # type: ignore

        self.user_data["google_id"] = "xxxxxxx"
        user = User(**self.user_data)
        provider = GoogleProvider('abc123')
        with self.assertRaises(AuthorizationError):
            provider._get_or_create_user(user)
