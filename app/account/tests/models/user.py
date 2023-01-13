from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist


class UserModelTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(  # type: ignore
            username='testuser',
            email='test@example.com',
            password='testpass',
            is_active=False
        )

    def test_activate(self):
        # Test that the user is inactive by default
        self.assertFalse(self.user.is_active)

        # Activate the user
        self.user.activate()

        # Check that the user is now active
        self.assertTrue(self.user.is_active)

    def test_login_success(self):
        # Ensure that the login function returns the expected output with valid data
        old_login = self.user.last_login
        login_response = self.user.login()
        self.assertIsInstance(login_response, dict)
        self.assertIn("token", login_response)
        self.assertIn("is_active", login_response)
        self.assertEqual(login_response["is_active"], False)
        self.assertNotEqual(self.user.last_login, old_login)

    def test_logout(self):
        # Create a user and log them in
        self.user.login()

        # Verify that the user has an auth token
        self.assertIsNotNone(self.user.auth_token)

        # Call the logout function
        self.user.logout()

        # Refresh the user object from the database
        self.user.refresh_from_db()

        try:
            self.user.auth_token
            assert False
        except ObjectDoesNotExist:
            assert True
