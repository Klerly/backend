
from wallet.modules.payment import Payment
from rest_framework import serializers
from core.exceptions import HttpValidationError


class PaymentInitializeSerializer(serializers.Serializer):
    amount = serializers.FloatField()

    def validate_amount(self, value):
        try:
            Payment.validate_integer_amount(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))


class PaymentChargeSerializer(serializers.Serializer):
    amount = serializers.FloatField()
    signature = serializers.CharField()

    def validate_amount(self, value):
        try:
            Payment.validate_integer_amount(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))
