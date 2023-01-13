from rest_framework import serializers
from wallet.models import TransactionModel


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionModel
        fields = (
            'reference',
            'amount',
            'created_at',
            'type',
            'status',
        )
