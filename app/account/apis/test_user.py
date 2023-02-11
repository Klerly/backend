from django.test import TestCase
from rest_framework.test import APIRequestFactory
from django.urls import reverse
from rest_framework.test import APIClient
from account.models import User, Seller
from account.serializers.user import (
    UserSerializer,
    SellerSerializer,
    PublicSellerSerializer
)
from account.apis.user import (
    UserAPI,
    SellerRetrieveUpdateAPI,
    SellerCreateAPI,
    PublicSellerRetrieveAPI,
    PublicListCreateAPI,

)
from rest_framework.permissions import IsAuthenticated
from account.permissions import IsVerified


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


class SellerAPITestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(  # type: ignore
            username='test@example.com',
            email='test@example.com',
            password='password',
            is_active=True,
            is_verified=True
        )

        self.create_url = reverse('account:account-seller-create')
        self.detail_url = reverse('account:account-seller-detail')

    def test_permission_classes_used(self):
        permissions = [IsAuthenticated, IsVerified]
        self.assertEqual(
            SellerRetrieveUpdateAPI.permission_classes, permissions)
        self.assertEqual(SellerCreateAPI.permission_classes, permissions)

    def test_serializer_class(self):
        self.assertEqual(
            SellerRetrieveUpdateAPI.serializer_class, SellerSerializer)
        self.assertEqual(
            SellerCreateAPI.serializer_class, SellerSerializer)

    def test_create(self):
        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.post(self.create_url, {
            'handle': 'testhandle',
            'name': 'Test Name',
        })
        self.assertEqual(response.status_code, 201)

    def test_retrieve(self):
        Seller.objects.create(  # type: ignore
            user=self.user,
            handle='testhandle',
            name='Test Name',
        )

        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.data.keys()),  # type: ignore
            set(SellerSerializer().fields.keys())
        )

    def test_update_not_found(self):
        """ Test that a 404 is returned if the seller does not exist."""
        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.patch(self.detail_url, {
            'name': 'Test Name',
        })
        self.assertEqual(response.status_code, 404)

    def test_update(self):

        Seller.objects.create(  # type: ignore
            user=self.user,
            handle='testhandle',
            name='Test Name',
        )

        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.patch(self.detail_url, {
            'name': 'Test Name 2',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Test Name 2')  # type: ignore


class PublicSellerAPITestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(  # type: ignore
            username='test@example.com',
            email='test@example.com',
            password='password',
            is_active=True,
            is_verified=True
        )
        self.seller = Seller.objects.create(  # type: ignore
            user=self.user,
            handle='testhandle',
            name='Test Name',
        )

        self.list_url = reverse('account:account-public-seller-list')
        self.detail_url = reverse('account:account-public-seller-detail', kwargs={
            'handle': self.seller.handle
        })

    def test_permission_classes_used(self):
        self.assertEqual(PublicSellerRetrieveAPI.permission_classes, [])
        self.assertEqual(PublicListCreateAPI.permission_classes, [])

    def test_serializer_class(self):
        self.assertEqual(
            PublicSellerRetrieveAPI.serializer_class, PublicSellerSerializer)
        self.assertEqual(
            PublicListCreateAPI.serializer_class, PublicSellerSerializer)

    def test_retrieve(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.data.keys()),  # type: ignore
            set(PublicSellerSerializer().fields.keys())
        )

    def test_list(self):
        response = self.client.get(self.list_url+'?search=test name')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.data['results']),  # type: ignore
            1
        )
        self.assertEqual(
            set(response.data['results'][0].keys()),  # type: ignore
            set(PublicSellerSerializer().fields.keys())
        )
