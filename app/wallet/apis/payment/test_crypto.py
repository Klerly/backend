from wallet.models import WalletModel, TransactionModel
from django.test import RequestFactory, TestCase
from unittest.mock import patch
from django.test import TestCase
from wallet.models import WalletModel, TransactionModel, CardModel
from rest_framework.test import APIClient
from account.models import User
from django.urls import reverse
from wallet.apis.payment.crypto import CryptoPaymentWebhookAPI
import json
import hmac
import hashlib


class CryptoPaymentInitializeAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(  # type: ignore
            username='testuser',
            password='password',
            is_verified=True
        )
        self.wallet = self.user.wallet
        self.url = reverse('wallet:payment-crypto-initialize')
        self.data = {'amount': 100}

    @patch('wallet.modules.payment.crypto.CryptoWalletPayment.initialize')
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


class CryptoPaymentVerifyAPITestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(  # type: ignore
            username='testuser',
            password='password',
            is_verified=True
        )
        self.wallet = self.user.wallet
        self.transaction = TransactionModel.objects.create(
            user=self.user,
            reference='123',
            status=TransactionModel.Status.PENDING,
            amount=100
        )
        self.url = reverse('wallet:payment-crypto-verify',
                           args=[self.transaction.reference])

    @patch('wallet.modules.payment.crypto.CryptoWalletPayment.verify')
    def test_verify_payment_success(self, mock_verify):
        mock_verify_return_value = {
            'status': True,
            'message': 'Payment successful'
        }
        mock_verify.return_value = mock_verify_return_value
        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,  # type: ignore
            mock_verify_return_value)
        mock_verify.assert_called_once_with(self.transaction)

    @patch('wallet.modules.payment.crypto.CryptoWalletPayment.verify')
    def test_verify_payment_failure(self, mock_verify):
        mock_verify_return_value = {
            'status': False,
            'message': 'We have not received your payment'
        }
        mock_verify.return_value = mock_verify_return_value
        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 400)
        mock_verify.assert_called_once_with(self.transaction)




    def test_verify_payment_not_found(self):
        url = reverse('wallet:payment-crypto-verify', args=['invalid'])
        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,  # type: ignore
            {'non_field_errors': ['Transaction not found']}
        )

    @patch('wallet.modules.payment.crypto.CryptoWalletPayment.verify')
    def test_verify_payment_already_completed(self, mock_verify):
        self.transaction.status = TransactionModel.Status.SUCCESS
        self.transaction.save()
        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        mock_verify.assert_not_called()


    def test_verify_payment_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)


class CryptoPaymentWebhookAPITest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = CryptoPaymentWebhookAPI.as_view()
        self.url = reverse('wallet:payment-crypto-webhook')
        self.request_data = {
            "id": "d6c4822a-964e-44db-94c4-8eae940ef065",
            "reference": "txn_123",
            "webhookType": "DEPOSIT_TRANSACTION"
        }
        self.lazerpay_signature = hmac.new(
            b'secret_key', json.dumps(self.request_data).encode('utf-8'),
            hashlib.sha256).hexdigest()
        self.transaction = TransactionModel.objects.create(
            user=User.objects.create_user(  # type: ignore
                username='testuser', password='password'),
            reference='txn_123',
            status=TransactionModel.Status.PENDING,
            amount=100
        )

    @patch('wallet.modules.payment.crypto.CryptoWalletPayment.success')
    def test_valid_request(self, mock_success):
        with self.settings(LAZERPAY_SECRET_KEY='secret_key'):
            request = self.factory.post(self.url, json.dumps(
                self.request_data), content_type='application/json')
            request.META['HTTP_X_LAZERPAY_SIGNATURE'] = self.lazerpay_signature

            response = self.view(request)
            mock_success.assert_called_once_with(
                self.transaction
            )
            self.assertEqual(response.status_code, 200)

    def test_invalid_hash(self):
        with self.settings(LAZERPAY_SECRET_KEY='secret_key'):
            request = self.factory.post(self.url, json.dumps(
                self.request_data), content_type='application/json')
            request.META['HTTP_X_LAZERPAY_SIGNATURE'] = "fake-hash"

            response = self.view(request)
            self.assertEqual(response.status_code, 403)

    # test that a logging error is raised when the transaction is not found

    @patch('logging.error')
    def test_transaction_not_found(self, mock_error):
        self.request_data['reference'] = 'txn_456'
        self.lazerpay_signature = hmac.new(
            b'secret_key', json.dumps(self.request_data).encode('utf-8'),
            hashlib.sha256).hexdigest()

        with self.settings(
            LAZERPAY_SECRET_KEY='secret_key'
        ):
            request = self.factory.post(self.url, json.dumps(
                self.request_data), content_type='application/json')
            request.META['HTTP_X_LAZERPAY_SIGNATURE'] = self.lazerpay_signature
            response = self.view(request)
            mock_error.assert_called_once()
            self.assertEqual(response.status_code, 200)
