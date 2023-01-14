from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from unittest import mock
from account.modules.mail.template import AccountMailTemplate
from account.models.verification import ResetPasswordTokenVerificationModel, EmailTokenVerificationModel
from urllib.parse import urlencode


class GeneralSignUpAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("account:account-general-signup")
        self.signup_data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "password123@32e12432"
        }

    def test_signup_with_valid_data(self):
        # Ensure that the API view creates a new user with valid data
        response = self.client.post(
            self.url, self.signup_data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.data) # type: ignore
        self.assertIn("is_verified", response.data) # type: ignore
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_signup_with_invalid_data(self):
        # Ensure that the API view returns a 400 status code with invalid data
        self.signup_data["email"] = ""
        response = self.client.post(
            self.url, self.signup_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(get_user_model().objects.count(), 0)


class GeneralSignInAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("account:account-general-signin")
        self.signin_data = {
            "email": "test@example.com",
            "username": "test@example.com",
            "password": "password123"
        }
        self.user = get_user_model().objects.create_user(  # type: ignore
            **self.signin_data
        )

    def test_signin_with_valid_data(self):
        # Ensure that the API view returns a success response with valid data
        response = self.client.post(
            self.url, self.signin_data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.user.login())  # type: ignore

    def test_signin_with_invalid_email(self):
        # Ensure that the API view returns a 400 status code with an invalid email
        self.signin_data["email"] = "invalid@example.com"
        response = self.client.post(
            self.url, self.signin_data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_signin_with_invalid_password(self):
        # Ensure that the API view returns a 400 status code with an invalid password
        self.signin_data["password"] = "invalidpassword"
        response = self.client.post(
            self.url, self.signin_data, format="json")
        self.assertEqual(response.status_code, 400)


class GeneralSignOutAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signout_url = reverse("account:account-general-signout")
        self.signin_data = {
            "email": "test@example.com",
            "password": "password123@@@@@12sq"
        }
        self.user = get_user_model().objects.create_user(  # type: ignore
            email="test@example.com",
            username="test@example.com",
            password="password123@@@@@12sq"
        )

    def test_signout(self):
        # Ensure that the API view logs out the authenticated user
        self.user.login()
        # assert that the user has an auth token
        self.assertIsNotNone(self.user.auth_token)

        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.post(self.signout_url, format="json")
        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        try:
            self.user.auth_token
            assert False
        except ObjectDoesNotExist:
            assert True


class SendVerificationEmailAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("account:account-general-send-verification-email")
        self.user = get_user_model().objects.create_user(   # type: ignore
            email="test@example.com",
            username="test@example.com",
            password="password123",
            is_active=False
        )
        self.client.force_authenticate(self.user)

    def test_send_verification_email_with_valid_data(self):
        # Ensure that the API view sends a verification email with valid data
        with mock.patch.object(AccountMailTemplate, "VerifyEmail", side_effect=None) as mock_send_verification_email:
            response = self.client.get(self.url)
            mock_send_verification_email.assert_called_once()
            self.assertEqual(response.status_code, 200)

    def test_send_verification_email_with_verified_account(self):
        self.user.is_verified = True
        self.user.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("already verified",
                      response.data["non_field_errors"][0])  # type: ignore


class CheckVerificationEmailTokenAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse(
            "account:account-general-check-verification-email-token")
        self.token = "123456"

        user = get_user_model().objects.create_user(  # type: ignore
            email="test@example.com",
            username="test@example.com",
            password="password123@@@@@12sq",
            is_verified=False,
        )
        user.email_verification_token = EmailTokenVerificationModel.objects.create(
            token=self.token,
            user=user
        )
        user.save()
        self.user = user
        self.client.force_authenticate(self.user)

    def test_check_verification_email_token_with_valid_data(self):
        # Ensure that the API view verifies the user's email with valid data
        data = {
            "token": self.token
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(get_user_model().objects.get(
            email="test@example.com").is_verified)  # type: ignore

    def test_check_verification_email_token_with_invalid_token(self):
        # Ensure that the API view returns a 400 status code with an invalid token
        data = {
            "token": "invalidtoken"
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(get_user_model().objects.get(
            email="test@example.com").is_verified)  # type: ignore

        self.assertIn(
            "token you entered is invalid",
            response.data["non_field_errors"][0]  # type: ignore
        )

    def test_check_verification_email_token_with_missing_token(self):
        # Ensure that the API view returns a 400 status code with a missing token
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(get_user_model().objects.get(
            email="test@example.com").is_verified)  # type: ignore
        self.assertIn(
            "Token is required",
            response.data["non_field_errors"][0]  # type: ignore
        )



    def test_check_verification_email_token_with_already_verified_email(self):
        # Ensure that the API view returns a 400 status code with an already verified email
        self.user.is_verified = True
        self.user.save()
        data = {
            "token": self.token,
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(get_user_model().objects.get(
            email="test@example.com").is_verified)  # type: ignore
        self.assertIn(
            "already verified",
            response.data["non_field_errors"][0]  # type: ignore
        )


class SendResetPasswordEmailAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("account:account-general-send-reset-password-email")
        self.user = get_user_model().objects.create_user(   # type: ignore
            email="test@example.com",
            username="test@example.com",
            password="password123",
            is_active=False
        )

    def test_send_rp_with_valid_data(self):
        # Ensure that the API view sends email with valid data
        with mock.patch.object(AccountMailTemplate, "ResetPassword", side_effect=None) as mock_send_rp:
            response = self.client.get(self.url, {"email": self.user.email})
            mock_send_rp.assert_called_once()
            self.assertEqual(response.status_code, 200)

    def test_send_rp_with_invalid_email(self):
        response = self.client.get(self.url, {"email": "1234s"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)  # type: ignore

    def test_send_rp_with_unused_email(self):
        response = self.client.get(self.url, {"email": "invalid@example.com"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)  # type: ignore


class CheckResetPasswordEmailTokenAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse(
            "account:account-general-check-reset-password-email-token")
        self.token = "123456"

        user = get_user_model().objects.create_user(  # type: ignore
            email="test@example.com",
            username="test@example.com",
            password="password123@@@@@12sq",
            is_active=True
        )
        user.reset_password_token = ResetPasswordTokenVerificationModel.objects.create(
            token=self.token,
            user=user
        )
        user.save()
        self.user = user

    def test_check_reset_password_email_token_with_valid_data(self):
        # Ensure that the API view validates the reset password token with valid data
        data = {
            "token": self.token,
            "email": "test@example.com"
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)

    def test_check_reset_password_email_token_with_invalid_token(self):
        # Ensure that the API view returns a 400 status code with an invalid token
        data = {
            "token": "invalidtoken",
            "email": "test@example.com"
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "reset password token is invalid",
            response.data["non_field_errors"][0]  # type: ignore
        )

    def test_check_reset_password_email_token_with_missing_token(self):
        # Ensure that the API view returns a 400 status code with a missing token
        data = {
            "email": "test@example.com"
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "A token and email are required",
            response.data["non_field_errors"][0]  # type: ignore
        )
