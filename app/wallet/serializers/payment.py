
from wallet.modules.payment import Payment
from rest_framework import serializers


class PaymentInitializeSerializer(serializers.Serializer):
    amount = serializers.IntegerField()

    def validate_amount(self, value):
        try:
            Payment.validate_integer_amount(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))
        return value


class PaymentChargeSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    signature = serializers.CharField()

    def validate_amount(self, value):
        try:
            Payment.validate_integer_amount(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))
        return value
