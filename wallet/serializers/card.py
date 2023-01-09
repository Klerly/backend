from wallet.models import CardModel
from rest_framework import serializers


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardModel
        read_only_fields = (
            "signature",
            "type",
            "last_four",
            "created_at",
        )
        fields = (
            "keep",
        ) + read_only_fields
