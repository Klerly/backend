from core.modules.payment import AbstractPayment
from decimal import Decimal
from django.test import TestCase
from account.models import User
from wallet.models import TransactionModel


class DummnyAbstractPayment(AbstractPayment):
    def __init__(self, user):
        self.user = user

    def initialize(self, amount: int):
        pass

    def verify(self, transaction: TransactionModel):
        pass

    def withdraw(self, amount: int):
        pass


class AbstractPaymentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='test@example.com',
            password='testpassword'
        )
        self.dummy = DummnyAbstractPayment(self.user)

    def test_init(self):
        self.assertEqual(self.dummy.user, self.user)

    def test_validate_integer_amount_invalid_type(self):
        with self.assertRaises(ValueError) as context:
            self.dummy.validate_integer_amount("1000")  # type: ignore
        self.assertEqual(str(context.exception), "Amount must be an integer")

    def test_validate_integer_amount_invalid_decimal(self):
        with self.assertRaises(ValueError) as context:
            self.dummy.validate_integer_amount(1000.5)  # type: ignore
        self.assertEqual(str(context.exception), "Amount must be an integer")

    def test_validate_integer_amount_negative(self):
        with self.assertRaises(ValueError) as context:
            self.dummy.validate_integer_amount(-1000)
        self.assertEqual(str(context.exception),
                         "Amount must be a positive number")

    def test_validate_decimal_amount_negative(self):
        with self.assertRaises(ValueError) as context:
            self.dummy.validate_decimal_amount(Decimal("-1000"))
        self.assertEqual(str(context.exception),
                         "Amount must be a positive number")
