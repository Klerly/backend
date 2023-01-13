from wallet.models import WalletModel, TransactionModel
from django.test import RequestFactory, TestCase
from unittest.mock import patch
from django.test import TestCase
from wallet.models import WalletModel, TransactionModel, CardModel
from rest_framework.test import APIClient
from account.models import User
from django.urls import reverse


class PaymentInitializeAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(  # type: ignore
            username='testuser', password='password')
        self.wallet = WalletModel.objects.create(user=self.user)
        self.url = reverse('wallet:payment-initialize')
        self.data = {'amount': 100}

    @patch('wallet.modules.payment.Payment.initialize')
    def test_initialize_payment(self, mock_initialize):
        mock_initialize.return_value = {'status': 'success'}
        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'status': 'success'})  # type: ignore
        mock_initialize.assert_called_once_with(100)

    def test_initialize_payment_unauthenticated(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 401)

    def test_initialize_payment_invalid_data(self):
        self.data = {'amount': 'invalid'}  # type: ignore
        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 400)


class PaymentVerifyAPITestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(  # type: ignore
            username='testuser', password='password')
        self.wallet = WalletModel.objects.create(user=self.user)
        self.transaction = TransactionModel.objects.create(
            user=self.user,
            reference='123',
            status=TransactionModel.Status.SUCCESS,
            amount=100
        )
        self.url = reverse('wallet:payment-verify',
                           args=[self.transaction.reference])

    @patch('wallet.modules.payment.Payment.verify')
    def test_verify_payment_success(self, mock_verify):
        mock_verify.return_value = {'status': 'success'}
        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'status': 'success'})  # type: ignore
        mock_verify.assert_called_once_with(self.transaction)

    def test_verify_payment_not_found(self):
        self.transaction.delete()
        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,  # type: ignore
            {'non_field_errors': ['Transaction not found']}
        )

    def test_verify_payment_already_completed(self):
        self.transaction.status = TransactionModel.Status.FAILED
        self.transaction.save()
        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,  # type: ignore
            {'non_field_errors': ['Transaction already completed']}
        )

    def test_verify_payment_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)


class PaymentChargeAPITestCase(TestCase):
    card_data = {
        "keep": False,
        "type": 'Visa',
        "last_four": '1234',
        "exp_month": '01',
        "exp_year": '2022',
        "authorization_code": 'authcode',
        "data": {'last4': '1234', 'exp_month': '01', 'exp_year': '2022',
                     'authorization_code': 'authcode', 'signature': 'signature'}
    }

    def setUp(self):
        self.factory = RequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(  # type: ignore
            username='testuser', password='password')
        self.wallet = WalletModel.objects.create(user=self.user, balance=1000)
        self.card = CardModel.objects.create(
            user=self.user,
            signature='signature',
            **self.card_data
        )
        self.url = reverse('wallet:payment-charge')
        self.client.force_authenticate(user=self.user)

    @patch('wallet.modules.payment.Payment.charge')
    def test_valid_charge(self, mock_charge):
        mock_charge.return_value = {'status': 'success'}
        data = {'amount': 100, 'signature': 'signature'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')  # type: ignore
        mock_charge.assert_called_with(self.card, 100)
