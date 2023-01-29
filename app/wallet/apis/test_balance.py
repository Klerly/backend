from django.test import TestCase
from rest_framework.test import APIClient
from wallet.models import WalletModel
from account.models import User
from django.urls import reverse
from decimal import Decimal


class WalletBalanceAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('wallet:balance')
        self.user = User.objects.create_user(  # type: ignore
            username='testuser', password='password',
            is_verified=True

        )
        self.wallet = WalletModel.objects.create(
            balance=112221000.12345678912345, user=self.user)

    def test_get_balance(self):
        """ Test that a user can get their balance

            Note: https://docs.djangoproject.com/en/4.1/ref/databases/#sqlite-decimal-handling
            SQLite has no real decimal internal type. 
            Decimal values are internally converted to the REAL data
            type (8-byte IEEE floating point number), as explained in 
            the SQLite datatypes documentation, so they dont support 
            correctly-rounded decimal floating point arithmetic.
        """
        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'balance': 112221000.12345679
        })
    def test_get_balance_unauthorized(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
