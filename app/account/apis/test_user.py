from django.test import TestCase
from rest_framework.test import APIRequestFactory
from django.urls import reverse
from rest_framework.test import APIClient
from account.models import User
from account.serializers.user import UserSerializer
from account.apis.user import UserAPI
from rest_framework.permissions import IsAuthenticated


class UserAPITestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(  # type: ignore
            username='test@example.com',
            email='test@example.com',
            password='password',
            is_active=False,
            is_verified=True
        )
        self.url = reverse('account:account-user')

    def test_permission_classes_used(self):
        self.assertEqual(UserAPI.permission_classes, [IsAuthenticated])

    def test_permission_classes_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_permission_classes_authenticated(self):
        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_serializer_class(self):
        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,  # type: ignore
            UserSerializer(self.user).data
        )
