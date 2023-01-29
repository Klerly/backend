from django.test import TestCase
from account.models import User
from unittest.mock import patch, MagicMock
from wallet.models import CardModel, WalletModel, TransactionModel
from wallet.modules.payment.crypto import CryptoWalletPayment
from core.modules.payment.crypto.lazerpay import LazerPay


class CryptoWalletPaymentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='test@example.com',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpassword'
        )
        self.payment = CryptoWalletPayment(self.user)

    @patch('wallet.modules.payment.crypto.CryptoWalletPayment._get_provider')
    def test_init(self, mock_get_provider):
        mock_get_provider.return_value = LazerPay(self.user)
        payment = CryptoWalletPayment(self.user)
        mock_get_provider.assert_called_once_with(self.user)
        self.assertEqual(payment.user, self.user)
        self.assertIsInstance(payment.provider, LazerPay)

    def test_success(self):
        transaction = TransactionModel.objects.create(
            user=self.user,
            amount=1000,
            status=TransactionModel.Status.PENDING
        )
        wallet = self.user.wallet  # type: ignore
        response = self.payment._success(transaction)  # type: ignore
        self.assertEqual(
            response, {"status": True, "message": "Payment successful"})
        transaction.refresh_from_db()
        self.assertEqual(transaction.status,
                         TransactionModel.Status.SUCCESS)
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, 1000)

    def test_failed(self):
        transaction = TransactionModel.objects.create(
            user=self.user,
            amount=1000,
            status=TransactionModel.Status.PENDING
        )

        response = self.payment._failed(transaction)  # type: ignore
        self.assertEqual(
            response, {"status": False, "message": "We have not received your payment"})
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, TransactionModel.Status.PENDING)

    def test_failed_already_success(self):
        transaction = TransactionModel.objects.create(
            user=self.user,
            amount=1000,
            status=TransactionModel.Status.SUCCESS
        )
        response = self.payment._failed(transaction)  # type: ignore
        self.assertEqual(
            response, {"status": False, "message": "We have not received your payment"})
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, TransactionModel.Status.SUCCESS)

    def test_failed_without_gateway_response(self):
        transaction = TransactionModel.objects.create(
            user=self.user,
            amount=1000,
            status=TransactionModel.Status.PENDING
        )
        response = self.payment._failed(transaction)  # type: ignore
        self.assertEqual(
            response, {"status": False, "message": "We have not received your payment"})
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, TransactionModel.Status.PENDING)

    @patch('wallet.modules.payment.crypto.CryptoWalletPayment._get_provider')
    def test_initialize(self, mock_get_provider):
        mock_provider = MagicMock()
        mock_provider.validate_integer_amount.return_value = 1000
        mock_provider.initialize.return_value = {"reference": "test_reference"}
        mock_get_provider.return_value = mock_provider
        data = CryptoWalletPayment(self.user).initialize(1000)
        mock_provider.validate_integer_amount.assert_called_with(1000)
        mock_get_provider.assert_called_once_with(self.user)
        mock_provider.initialize.assert_called_once_with(1000)
        self.assertEqual(data, {"reference": "test_reference"})

    @patch('wallet.modules.payment.crypto.CryptoWalletPayment._get_provider')
    def test_verify(self, mock_get_provider):
        mock_provider = MagicMock()
        mock_provider.verify.return_value = True
        mock_get_provider.return_value = mock_provider
        transaction = TransactionModel.objects.create(
            user=self.user,
            amount=1000,
            reference="test_reference",
            status=TransactionModel.Status.PENDING
        )
        with patch.object(CryptoWalletPayment, '_success') as mock_success:
            CryptoWalletPayment(self.user).verify(transaction)
            mock_success.assert_called_once_with(transaction)

    @patch('wallet.modules.payment.crypto.CryptoWalletPayment._get_provider')
    def test_verify_failed(self, mock_get_provider):
        mock_provider = MagicMock()
        mock_provider.verify.return_value = False
        mock_get_provider.return_value = mock_provider
        transaction = TransactionModel.objects.create(
            user=self.user,
            amount=1000,
            reference="test_reference",
            status=TransactionModel.Status.PENDING
        )
        with patch.object(CryptoWalletPayment, '_failed') as mock_failed:
            CryptoWalletPayment(self.user).verify(transaction)
            mock_failed.assert_called_once_with(
                transaction)
