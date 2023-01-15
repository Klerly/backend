from django.urls import reverse
from rest_framework.test import APIClient, APIRequestFactory
from account.models import User
from django.test import TestCase
from wallet.models import TransactionModel
from wallet.apis.transaction import TransactionRetrieveAPI, TransactionListAPI


class TransactionListAPITestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(  # type: ignore
            username='testuser',
            password='password',
            is_verified=True

        )
        self.client.force_authenticate(user=self.user)
        self.transaction1 = TransactionModel.objects.create(
            user=self.user,
            amount=1000,
            reference='ref1'
        )
        self.transaction2 = TransactionModel.objects.create(
            user=self.user,
            amount=2000,
            reference='ref2'
        )
        self.transaction_list_url = reverse('wallet:transaction-list')
        self.transaction_detail_url = reverse(
            'wallet:transaction-detail', args=[self.transaction1.reference])

    def test_get_queryset(self):
        view = TransactionListAPI()
        view.request = self.factory.get(self.transaction_list_url)
        view.request.user = self.user
        view.kwargs = {'pk': self.transaction1.reference}
        queryset = view.get_queryset()
        self.assertEqual(queryset.count(), 2)
        self.assertEqual(queryset.first(), self.transaction1)

    def test_get_queryset_different_user(self):
        user2 = User.objects.create_user(  # type: ignore
            username='testuser2',
            email='testuser2@mail.com',
            password='password'
        )
        view = TransactionListAPI()
        view.request = self.factory.get(self.transaction_list_url)
        view.request.user = user2
        queryset = view.get_queryset()
        self.assertEqual(queryset.count(), 0)

    def test_list_transactions(self):
        response = self.client.get(self.transaction_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)  # type: ignore


class TransactionRetrieveAPITestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(  # type: ignore
            username='testuser',
            password='password',
            is_verified=True

        )
        self.client.force_authenticate(user=self.user)
        self.transaction1 = TransactionModel.objects.create(
            user=self.user,
            amount=1000,
            reference='ref1'
        )
        self.transaction2 = TransactionModel.objects.create(
            user=self.user,
            amount=2000,
            reference='ref2'
        )
        self.transaction_list_url = reverse('wallet:transaction-list')
        self.transaction_detail_url = reverse(
            'wallet:transaction-detail', args=[self.transaction1.reference])

    def test_get_queryset(self):
        view = TransactionRetrieveAPI()
        view.request = self.factory.get(self.transaction_list_url)
        view.request.user = self.user
        view.kwargs = {'pk': self.transaction1.reference}
        queryset = view.get_queryset()
        self.assertEqual(queryset.count(), 2)
        self.assertEqual(queryset.first(), self.transaction1)

    def test_get_queryset_different_user(self):
        user2 = User.objects.create_user(  # type: ignore
            username='testuser2',
            email='testuser2@mail.com',
            password='password'
        )
        view = TransactionRetrieveAPI()
        view.request = self.factory.get(self.transaction_list_url)
        view.request.user = user2
        queryset = view.get_queryset()
        self.assertEqual(queryset.count(), 0)

    def test_retrieve_transaction(self):
        response = self.client.get(self.transaction_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data  # type: ignore
                         ['amount'], 1000)

    def test_update_transaction(self):
        data = {'amount': 3000}
        response = self.client.patch(self.transaction_detail_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data  # type: ignore
                         ['amount'], 3000)

    def test_delete_transaction(self):
        self.assertEqual(TransactionModel.objects.count(), 2)
        response = self.client.delete(self.transaction_detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(TransactionModel.objects.count(), 1)
