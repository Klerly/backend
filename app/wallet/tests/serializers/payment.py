
from django.test import TestCase
from unittest.mock import patch
from wallet.modules.payment import Payment
from wallet.serializers.payment import PaymentInitializeSerializer, PaymentChargeSerializer


class PaymentInitializeSerializerTest(TestCase):
    def setUp(self):
        self.valid_data = {'amount': 1000.00}
        self.invalid_data = {'amount': '22.00'}

    def test_initialize_validation(self):
        serializer = PaymentInitializeSerializer(
            data=self.valid_data)  # type: ignore
        with patch.object(Payment, 'validate_integer_amount', return_value=True) as mocked_validate:
            self.assertTrue(serializer.is_valid())
            mocked_validate.assert_called_with(self.valid_data['amount'])

    def test_initialize_validation_error(self):
        serializer = PaymentInitializeSerializer(
            data=self.invalid_data)  # type: ignore
        with patch.object(Payment, 'validate_integer_amount', side_effect=ValueError('Invalid amount')) as mocked_validate:
            self.assertFalse(serializer.is_valid())

            self.assertEqual(serializer.errors, {'amount': ['Invalid amount']})
            mocked_validate.assert_called_with(
                float(self.invalid_data['amount']))


class PaymentChargeSerializerTest(TestCase):
    def setUp(self):
        self.valid_data = {'amount': 1000.00}
        self.invalid_data = {'amount': '22.00'}

    def test_charge_validation(self):
        valid_data = {
            'amount': self.valid_data["amount"], 'signature': 'valid_signature'}
        serializer = PaymentChargeSerializer(data=valid_data)  # type: ignore
        with patch.object(Payment, 'validate_integer_amount', return_value=True) as mocked_validate:
            self.assertTrue(serializer.is_valid())
            mocked_validate.assert_called_with(valid_data['amount'])

    def test_charge_validation_error(self):
        invalid_data = {
            'amount': self.invalid_data["amount"], 'signature': 'valid_signature'}
        serializer = PaymentChargeSerializer(data=invalid_data)  # type: ignore
        with patch.object(Payment, 'validate_integer_amount', side_effect=ValueError('Invalid amount')) as mocked_validate:
            self.assertFalse(serializer.is_valid())
            self.assertEqual(serializer.errors, {'amount': ['Invalid amount']})
            mocked_validate.assert_called_with(
                float(invalid_data['amount'])
            )

    def test_fail(self):
        assert 1 == 0
