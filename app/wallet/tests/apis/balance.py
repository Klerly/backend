from django.test import TestCase
from rest_framework.test import APIClient
from wallet.models import WalletModel
from account.models import User
from django.urls import reverse


class WalletBalanceAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('wallet:balance')
        self.user = User.objects.create_user(  # type: ignore
            username='testuser', password='password',
            is_verified=True

        )
        self.wallet = WalletModel.objects.create(
            balance=1000.00, user=self.user)

    def test_get_balance(self):
        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'balance': 1000.00})  # type: ignore

    def test_get_balance_unauthorized(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
