from django.test import TestCase
from unittest.mock import patch
from unittest import mock
from account.models import User
from core.modules.payment.crypto.lazerpay import LazerPay
from wallet.models import TransactionModel
from requests.models import Response


class LazerPayTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='test@example.com', password='testpassword')
        self.lazerpay = LazerPay(user=self.user)

    def test_init(self):
        self.assertEqual(self.lazerpay.user, self.user)
        self.assertEqual(self.lazerpay.coin, 'USDT')

    def test_handle_response_success(self):
        response = Response()
        response.status_code = 200
        response._content = b'{"status": "success", "data": "valid_data"}'

        self.assertEqual(self.lazerpay._handle_response(
            response), 'valid_data')

    def test_handle_response_failure(self):
        response = Response()
        response.status_code = 400
        response._content = b'{"status": "failure", "message": "invalid_data"}'

        self.assertRaises(Exception, self.lazerpay._handle_response, response)

    def test_make_request(self):
        with self.settings(LAZERPAY_PUBLIC_KEY='public_key', LAZERPAY_SECRET_KEY='secret_key'):
            with patch('requests.request') as mock_request:
                response = Response()
                response.status_code = 200
                response._content = b'{"status": "success", "data": "valid_data"}'
                mock_request.return_value = response

                method = 'POST'
                url = 'https://x.y/z'
                payload = {'a': 'b'}
                response = self.lazerpay._make_request(
                    method, url, payload=payload)
                self.assertEqual(response, 'valid_data')

                mock_request.assert_called_with(method, url,
                                                headers={
                                                    'x-api-key': 'public_key',
                                                    'Authorization': 'Bearer secret_key',
                                                },
                                                data=payload
                                                )

    @patch('core.modules.payment.crypto.lazerpay.LazerPay._make_request')
    def test_initialize(self, mock_make_request, ):
        mock_make_request.return_value = 'valid_data'
        amount = 1000
        response = self.lazerpay.initialize(amount)
        self.assertEqual(response, 'valid_data')

        transaction = TransactionModel.objects.get(
            user=self.user
        )
        self.assertEqual(transaction.status, TransactionModel.Status.PENDING)
        self.assertEqual(transaction.amount, 1000)
        self.assertEqual(transaction.type, TransactionModel.Type.DEPOSIT)
        self.assertEqual(transaction.reference, mock.ANY)

        mock_make_request.assert_called_once()
        mock_make_request.assert_called_with(
            'post',
            LazerPay.URLS.INITIIALIZE,
            {
                "customer_name": "{user.first_name} {user.last_name}".format(user=self.user),
                "customer_email": self.user.email,
                "coin": self.lazerpay.coin,
                "currency": "USD",
                "amount": transaction.amount
            }
        )

    @patch('core.modules.payment.crypto.lazerpay.LazerPay._make_request')
    def test_initialize_validation_error(self, mock_make_request):
        amount = -1000
        self.assertRaises(ValueError, self.lazerpay.initialize, amount)
        mock_make_request.assert_not_called()

    @patch('core.modules.payment.crypto.lazerpay.LazerPay._make_request')
    def test_initialize_error_response(self, mock_make_request):
        mock_make_request.side_effect = Exception('Invalid amount')
        amount = 1000
        self.assertRaises(Exception, self.lazerpay.initialize, amount)

    @patch('core.modules.payment.crypto.lazerpay.LazerPay._make_request')
    def test_verify(self, mock_make_request):
        with self.settings(DEBUG=True):
            mock_make_request.return_value = {
                "status": "confirmed",
                "amountPaid": 1000,
                "actualAmount": 1000,
                "network": "testnet"
            }
            reference = 'valid_reference'
            success = self.lazerpay.verify(reference)
            self.assertTrue(success)
            mock_make_request.assert_called_once()

    @patch('core.modules.payment.crypto.lazerpay.LazerPay._make_request')
    def test_verify_failed_wrong_network(self, mock_make_request):
        with self.settings(DEBUG=False):
            mock_make_request.return_value = {
                "status": "confirmed",
                "amountPaid": 1000,
                "actualAmount": 1000,
                "network": "testnet"
            }
            reference = 'valid_reference'
            success = self.lazerpay.verify(reference)
            self.assertFalse(success)
            mock_make_request.assert_called_once()

    @patch('core.modules.payment.crypto.lazerpay.LazerPay._make_request')
    def test_verify_failed_bad_status(self, mock_make_request):
        with self.settings(DEBUG=True):
            mock_make_request.return_value = {
                "status": "incomplete",
                "amountPaid": 1000,
                "actualAmount": 1000,
                "network": "testnet"
            }
            reference = 'valid_reference'
            success = self.lazerpay.verify(reference)
            self.assertFalse(success)
            mock_make_request.assert_called_once()

    @patch('core.modules.payment.crypto.lazerpay.LazerPay._make_request')
    def test_verify_failed_different_amounts(self, mock_make_request):
        with self.settings(DEBUG=True):
            mock_make_request.return_value = {
                "status": "confirmed",
                "amountPaid": 1000,
                "actualAmount": 2000,
                "network": "testnet"
            }
            reference = 'valid_reference'
            success = self.lazerpay.verify(reference)
            self.assertFalse(success)
            mock_make_request.assert_called_once()
