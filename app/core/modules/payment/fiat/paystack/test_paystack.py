from django.test import TestCase
from unittest.mock import patch
from unittest import mock
from account.models import User
from core.modules.payment.fiat.paystack import Paystack
from django.conf import settings
from wallet.models import TransactionModel


class PaystackTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='test@example.com', password='testpassword')
        self.paystack = Paystack(user=self.user)

    def test_convert_to_kobo(self):
        amount = 1000
        kobo_amount = self.paystack._convert_to_kobo(amount)
        self.assertEqual(kobo_amount, 100000)

    def test_convert_to_kobo_negative_amount(self):
        amount = -1000
        self.assertRaises(ValueError, self.paystack._convert_to_kobo, amount)

    def test_convert_to_kobo_decimal_amount(self):
        amount = 1000.50
        self.assertRaises(ValueError, self.paystack._convert_to_kobo, amount)

    def test_convert_to_kobo_string_amount(self):
        amount = '1000'
        self.assertRaises(ValueError, self.paystack._convert_to_kobo, amount)

    def test_handle_response_success(self):
        response = {'status': True, 'data': 'valid_data'}
        self.assertEqual(self.paystack._handle_response(
            response), 'valid_data')

    def test_handle_response_failure(self):
        response = {'status': False, 'message': 'invalid_data'}
        self.assertRaises(Exception, self.paystack._handle_response, response)

    def test_handle_response_invalid(self):
        response = {'status': 'invalid'}
        self.assertRaises(Exception, self.paystack._handle_response, response)

    def test_handle_response_missing_data(self):
        response = {}  # type: ignore
        self.assertRaises(Exception, self.paystack._handle_response, response)

    @patch('paystackapi.transaction.Transaction.initialize')
    @patch('core.modules.payment.fiat.paystack.Paystack._handle_response')
    def test_initialize(self, mock_handle_response, mock_initialize):
        mock_initialize.return_value = {'status': True, 'data': 'valid_data'}
        mock_handle_response.return_value = 'valid_data'
        amount = 1000
        response = self.paystack.initialize(amount)
        self.assertEqual(response, 'valid_data')

        transaction = TransactionModel.objects.get(
            user=self.user
        )
        self.assertEqual(transaction.status, TransactionModel.Status.PENDING)
        self.assertEqual(transaction.amount, 1000)
        self.assertEqual(transaction.reference, mock.ANY)

        mock_initialize.assert_called_with(
            email=self.user.email,
            amount=100000,
            callback_url=settings.PAYSTACK_CALLBACK_URL,
            reference=transaction.reference,
        )

        mock_handle_response.assert_called_once()

    @patch('paystackapi.transaction.Transaction.initialize')
    @patch('core.modules.payment.fiat.paystack.Paystack._handle_response')
    def test_initialize_validation_error(self, mock_handle_response, mock_initialize):
        amount = -1000
        self.assertRaises(ValueError, self.paystack.initialize, amount)
        mock_handle_response.assert_not_called()
        mock_initialize.assert_not_called()

    @patch('paystackapi.transaction.Transaction.initialize')
    @patch('core.modules.payment.fiat.paystack.Paystack._handle_response')
    def test_initialize_error_response(self, mock_handle_response, mock_initialize):
        mock_initialize.return_value = {
            'status': False, 'message': 'Invalid amount'}
        mock_handle_response.side_effect = Exception('Invalid amount')
        amount = 1000
        self.assertRaises(Exception, self.paystack.initialize, amount)
        mock_initialize.assert_called_with(
            email=self.user.email,
            amount=100000,
            callback_url=settings.PAYSTACK_CALLBACK_URL,
            # assert that it was clled with a uuid as reference
            reference=mock.ANY,
        )
        mock_handle_response.assert_called_once()

    @patch('core.modules.payment.fiat.paystack.Paystack._convert_to_kobo')
    @patch('paystackapi.transaction.Transaction.charge')
    @patch('core.modules.payment.fiat.paystack.Paystack._handle_response')
    def test_charge(self, mock_handle_response, mock_charge, mock_convert_to_kobo):
        transaction = TransactionModel.objects.create(
            user=self.user,
            amount=1000,
            reference='test',
            status=TransactionModel.Status.PENDING,
            type=TransactionModel.Type.DEPOSIT,
        )

        mock_convert_to_kobo.return_value = 100000
        mock_charge.return_value = {
            'status': True, 'data': {'status': 'success'}}
        mock_handle_response.return_value = {'status': 'success'}
        amount = 1000
        authorization_code = 'valid_code'
        success, response = self.paystack.charge(
            amount, authorization_code, transaction)
        self.assertTrue(success)
        self.assertEqual(response, {'status': 'success'})
        mock_convert_to_kobo.assert_called_with(amount)
        mock_charge.assert_called_with(
            email=self.user.email,
            amount=100000,
            authorization_code=authorization_code,
            reference=transaction.reference
        )
        mock_handle_response.assert_called_once()

    @patch('paystackapi.transaction.Transaction.charge')
    @patch('core.modules.payment.fiat.paystack.Paystack._handle_response')
    def test_charge_validation_error(self, mock_handle_response, mock_charge):
        transaction = TransactionModel.objects.create(
            user=self.user,
            amount=1000,
            reference='test',
            status=TransactionModel.Status.PENDING,
            type=TransactionModel.Type.DEPOSIT,
        )

        amount = -1000
        authorization_code = 'valid_code'
        self.assertRaises(ValueError, self.paystack.charge,
                          amount, authorization_code, transaction)
        mock_charge.assert_not_called()
        mock_handle_response.assert_not_called()

    @patch('core.modules.payment.fiat.paystack.Paystack._convert_to_kobo')
    @patch('paystackapi.transaction.Transaction.charge')
    @patch('core.modules.payment.fiat.paystack.Paystack._handle_response')
    def test_charge_error_response(self, mock_handle_response, mock_charge, mock_convert_to_kobo):
        transaction = TransactionModel.objects.create(
            user=self.user,
            amount=1000,
            reference='test',
            status=TransactionModel.Status.PENDING,
            type=TransactionModel.Type.DEPOSIT,
        )

        mock_convert_to_kobo.return_value = 100000
        mock_charge.return_value = {
            'status': False, 'message': 'Invalid amount'}
        mock_handle_response.side_effect = Exception('Invalid amount')
        amount = 1000
        authorization_code = 'valid_code'
        self.assertRaises(Exception, self.paystack.charge,
                          amount, authorization_code, transaction)
        mock_convert_to_kobo.assert_called_with(amount)
        mock_charge.assert_called_with(
            email=self.user.email, amount=100000, authorization_code=authorization_code,
            reference=transaction.reference)
        mock_handle_response.assert_called_once()

    @patch('paystackapi.transaction.Transaction.verify')
    @patch('core.modules.payment.fiat.paystack.Paystack._handle_response')
    def test_verify(self, mock_handle_response, mock_verify):
        mock_verify.return_value = {
            'status': True, 'data': {'status': 'success'}}
        mock_handle_response.return_value = {'status': 'success'}
        reference = 'valid_reference'
        success, response = self.paystack.verify(reference)
        self.assertTrue(success)
        self.assertEqual(response, {'status': 'success'})
        mock_verify.assert_called_with(reference='valid_reference')
        mock_handle_response.assert_called_once()

    @patch('paystackapi.transaction.Transaction.verify')
    @patch('core.modules.payment.fiat.paystack.Paystack._handle_response')
    def test_verify_failed(self, mock_handle_response, mock_verify):
        mock_verify.return_value = {
            'status': True, 'data': {'status': 'failed'}}
        mock_handle_response.return_value = {'status': 'failed'}
        reference = 'valid_reference'
        success, response = self.paystack.verify(reference)
        self.assertFalse(success)
        self.assertEqual(response, {'status': 'failed'})
        mock_verify.assert_called_with(reference='valid_reference')
        mock_handle_response.assert_called_once()

    @patch('paystackapi.transaction.Transaction.verify')
    @patch('core.modules.payment.fiat.paystack.Paystack._handle_response')
    def test_verify_error_response(self, mock_handle_response, mock_verify):
        mock_verify.return_value = {
            'status': False, 'message': 'Transaction not found'}
        mock_handle_response.side_effect = Exception('Transaction not found')
        reference = 'invalid_reference'
        self.assertRaises(Exception, self.paystack.verify, reference)
        mock_verify.assert_called_with(reference='invalid_reference')
        mock_handle_response.assert_called_once()
