from django.test import TestCase
from account.models import User
from unittest.mock import patch, MagicMock
from wallet.models import CardModel, WalletModel, TransactionModel
from wallet.modules.payment.fiat import FiatWalletPayment
from core.modules.payment.fiat.paystack import Paystack


class FiatWalletPaymentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='test@example.com',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpassword'
        )
        self.payment = FiatWalletPayment(self.user)

    @patch('wallet.modules.payment.fiat.FiatWalletPayment._get_provider')
    def test_init(self, mock_get_provider):
        mock_get_provider.return_value = Paystack(self.user)
        payment = FiatWalletPayment(self.user)
        mock_get_provider.assert_called_once_with(self.user)
        self.assertEqual(payment.user, self.user)
        self.assertIsInstance(payment.provider, Paystack)

    def test_add_card(self):
        data = {
            "channel": "card",
            "authorization": {
                "reusable": True,
                "last4": "4321",
                "exp_month": "12",
                "exp_year": "2023",
                "authorization_code": "AUTH_abcdef",
                "signature": "SIG_abcdef",
            }
        }
        self.payment._add_card(data)  # type: ignore
        card = CardModel.objects.get(user=self.user)
        self.assertEqual(card.last_four, "4321")
        self.assertEqual(card.exp_month, "12")
        self.assertEqual(card.exp_year, "2023")
        self.assertEqual(card.authorization_code, "AUTH_abcdef")
        self.assertEqual(card.signature, "SIG_abcdef")

    def test_add_card_with_wrong_channel(self):
        data = {
            "channel": "bank",
            "authorization": {
                "reusable": True,
                "last4": "4321",
                "exp_month": "12",
                "exp_year": "2023",
                "authorization_code": "AUTH_abcdef",
                "signature": "SIG_abcdef",
            }
        }
        self.payment._add_card(data)  # type: ignore
        self.assertEqual(CardModel.objects.count(), 0)

    def test_add_card_with_not_reusable(self):
        data = {
            "channel": "card",
            "authorization": {
                "reusable": False,
                "last4": "4321",
                "exp_month": "12",
                "exp_year": "2023",
                "authorization_code": "AUTH_abcdef",
                "signature": "SIG_abcdef",
            }
        }
        self.payment._add_card(data)  # type: ignore
        self.assertEqual(CardModel.objects.count(), 0)

    def test_success(self):
        transaction = TransactionModel.objects.create(
            user=self.user,
            amount=1000,
            status=TransactionModel.Status.PENDING
        )
        data = {
            "channel": "card",
            "authorization": {
                "reusable": True,
                "last4": "4321",
                "exp_month": "12",
                "exp_year": "2023",
                "authorization_code": "AUTH_abcdef",
                "signature": "SIG_abcdef",
            }
        }
        wallet = self.user.wallet  # type: ignore
        with patch.object(FiatWalletPayment, '_add_card') as mock_add_card:
            response = self.payment._success(transaction, data)  # type: ignore
            mock_add_card.assert_called_once_with(data)
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
        data = {
            "gateway_response": "Transaction declined by bank"
        }
        response = self.payment._failed(transaction, data)  # type: ignore
        self.assertEqual(
            response, {"status": False, "message": "Transaction declined by bank"})
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, TransactionModel.Status.FAILED)

    def test_failed_already_success(self):
        transaction = TransactionModel.objects.create(
            user=self.user,
            amount=1000,
            status=TransactionModel.Status.SUCCESS
        )
        data = {
            "gateway_response": "Transaction declined by bank"
        }
        response = self.payment._failed(transaction, data)  # type: ignore
        self.assertEqual(
            response, {"status": False, "message": "Transaction declined by bank"})
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, TransactionModel.Status.SUCCESS)

    def test_failed_without_gateway_response(self):
        transaction = TransactionModel.objects.create(
            user=self.user,
            amount=1000,
            status=TransactionModel.Status.PENDING
        )
        data = {}  # type: ignore
        response = self.payment._failed(transaction, data)  # type: ignore
        self.assertEqual(
            response, {"status": False, "message": "We have not received your payment"})
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, TransactionModel.Status.FAILED)

    @patch('wallet.modules.payment.fiat.FiatWalletPayment._get_provider')
    def test_initialize(self, mock_get_provider):
        mock_provider = MagicMock()
        mock_provider.validate_integer_amount.return_value = 1000
        mock_provider.initialize.return_value = {"reference": "test_reference"}
        mock_get_provider.return_value = mock_provider
        data = FiatWalletPayment(self.user).initialize(1000)
        mock_provider.validate_integer_amount.assert_called_with(1000)
        mock_get_provider.assert_called_once_with(self.user)
        mock_provider.initialize.assert_called_once_with(1000)
        self.assertEqual(data, {"reference": "test_reference"})

    @patch('wallet.modules.payment.fiat.FiatWalletPayment._get_provider')
    def test_verify(self, mock_get_provider):
        mock_provider = MagicMock()
        mock_provider.verify.return_value = (True, {
            "channel": "card",
            "authorization": {
                "reusable": True,
                "last4": "4321",
                "exp_month": "12",
                "exp_year": "2023",
                "authorization_code": "AUTH_abcdef",
                "signature": "SIG_abcdef",
            }
        })
        mock_get_provider.return_value = mock_provider
        transaction = TransactionModel.objects.create(
            user=self.user,
            amount=1000,
            reference="test_reference",
            status=TransactionModel.Status.PENDING
        )
        with patch.object(FiatWalletPayment, '_success') as mock_success:
            FiatWalletPayment(self.user).verify(transaction)
            mock_success.assert_called_once_with(
                transaction, mock_provider.verify.return_value[1])

    @patch('wallet.modules.payment.fiat.FiatWalletPayment._get_provider')
    def test_verify_failed(self, mock_get_provider):
        mock_provider = MagicMock()
        mock_provider.verify.return_value = (False, {
            "gateway_response": "Transaction declined by bank"
        })
        mock_get_provider.return_value = mock_provider
        transaction = TransactionModel.objects.create(
            user=self.user,
            amount=1000,
            reference="test_reference",
            status=TransactionModel.Status.PENDING
        )
        with patch.object(FiatWalletPayment, '_failed') as mock_failed:
            FiatWalletPayment(self.user).verify(transaction)
            mock_failed.assert_called_once_with(
                transaction, mock_provider.verify.return_value[1])

    @patch('wallet.modules.payment.fiat.FiatWalletPayment._get_provider')
    def test_charge(self, mock_get_provider):
        mock_provider = MagicMock()
        mock_provider.validate_integer_amount.return_value = 1000
        mock_provider.charge.return_value = (True, {
            "channel": "card",
            "reference": "test_reference",
            "authorization": {
                "reusable": True,
                "last4": "4321",
                "exp_month": "12",
                "exp_year": "2023",
                "authorization_code": "AUTH_abcdef",
                "signature": "SIG_abcdef",
            },
        })
        mock_get_provider.return_value = mock_provider
        card = CardModel.objects.create(
            user=self.user,
            data={
                "reusable": True,
                "last4": "4321",
                "exp_month": "12",
                "exp_year": "2023",
                "authorization_code": "AUTH_abcdef",
                "signature": "SIG_abcdef",
            }
        )
        with patch.object(FiatWalletPayment, '_success') as mock_success:
            FiatWalletPayment(self.user).charge(card, 1000)
            mock_success.assert_called_once_with(
                mock_success.call_args[0][0],
                mock_provider.charge.return_value[1]
            )

    @patch('wallet.modules.payment.fiat.FiatWalletPayment._get_provider')
    def test_charge_failed(self, mock_get_provider):
        mock_provider = MagicMock()
        mock_provider.validate_integer_amount.return_value = 1000

        mock_provider.charge.return_value = (False, {
            "reference": "test_reference",
            "gateway_response": "Transaction declined by bank"
        })
        mock_get_provider.return_value = mock_provider
        card = CardModel.objects.create(
            user=self.user,
            data={
                "reusable": True,
                "last4": "4321",
                "exp_month": "12",
                "exp_year": "2023",
                "authorization_code": "AUTH_abcdef",
                "signature": "SIG_abcdef",
            }
        )
        with patch.object(FiatWalletPayment, '_failed') as mock_failed:
            FiatWalletPayment(self.user).charge(card, 1000)
            mock_failed.assert_called_once_with(
                mock_failed.call_args[0][0],
                mock_provider.charge.return_value[1]
            )
