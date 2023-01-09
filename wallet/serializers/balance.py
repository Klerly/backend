from rest_framework import serializers


class WalletBalanceSerializer(serializers.Serializer):
    balance = serializers.FloatField()
