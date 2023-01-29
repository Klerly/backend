import json

from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

from account.serializers.auth.general import (
    GeneralSignUpSerializer, GeneralSignInSerializer
)

User = get_user_model()


class GeneralSignUpSerializerTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_data = {
            "email": "test@example.com",
            "username": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "password123@123213"
        }

    def test_signup_with_valid_data(self):
        # Ensure that the serializer accepts valid data
        serializer = GeneralSignUpSerializer(
            data=self.signup_data)  # type: ignore

        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_signup_with_duplicate_email(self):
        # Ensure that the serializer rejects data with a duplicate email
        User.objects.create_user(**self.signup_data)  # type: ignore
        serializer = GeneralSignUpSerializer(
            data=self.signup_data)  # type: ignore
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_signup_with_invalid_password(self):
        # Ensure that the serializer rejects data with an invalid password
        self.signup_data["password"] = "short"
        serializer = GeneralSignUpSerializer(
            data=self.signup_data)  # type: ignore
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_signup_creates_user(self):
        # Ensure that the serializer creates a new user
        serializer = GeneralSignUpSerializer(
            data=self.signup_data)  # type: ignore
        serializer.is_valid()
        serializer.save()
        self.assertEqual(User.objects.count(), 1)


class GeneralSignInSerializerTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_data = {
            "email": "test@example.com",
            "username": "test@example.com",
            "password": "password123"
        }
        self.user = get_user_model().objects.create_user(  # type: ignore
            **self.signup_data
        )

    def test_signin_with_valid_data(self):
        # Ensure that the serializer accepts valid data
        serializer = GeneralSignInSerializer(
            data=self.signup_data)  # type: ignore
        self.assertTrue(serializer.is_valid())

    def test_signin_with_invalid_email(self):
        # Ensure that the serializer rejects data with an invalid email
        self.signup_data["email"] = "invalid@example.com"
        serializer = GeneralSignInSerializer(
            data=self.signup_data)  # type: ignore
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_signin_with_invalid_password(self):
        # Ensure that the serializer rejects data with an invalid password
        self.signup_data["password"] = "invalidpassword"
        serializer = GeneralSignInSerializer(
            data=self.signup_data)  # type: ignore
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors["non_field_errors"][0])

    def test_signin_validates_user_credentials(self):
        # Ensure that the serializer validates the user's credentials
        serializer = GeneralSignInSerializer(
            data=self.signup_data)  # type: ignore
        serializer.is_valid()
        # type: ignore
        self.assertEqual(
            serializer.validated_data["user"],  # type: ignore
            self.user
        )
