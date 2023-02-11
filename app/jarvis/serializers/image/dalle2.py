from rest_framework import serializers
from jarvis.models import (
    AbstractPromptModel,
    Dalle2PromptModel,
    PromptOutputModel
)
from jarvis.serializers.abstract import (
    AbstractPromptSellerSerializer,
    AbstractPromptBuyerSerializer
)
from typing import Optional, Union


class Dalle2PromptSellerSerializer(AbstractPromptSellerSerializer):
    class Meta(AbstractPromptSellerSerializer.Meta):
        model = Dalle2PromptModel
        fields = AbstractPromptSellerSerializer.Meta.fields


class Dalle2PromptBuyerSerializer(AbstractPromptBuyerSerializer):
    size = serializers.ChoiceField(
        choices=Dalle2PromptModel.ImageSizes.values,
        default=Dalle2PromptModel.ImageSizes.MEDIUM,
        write_only=True
    )

    class Meta(AbstractPromptBuyerSerializer.Meta):
        model = Dalle2PromptModel
        fields = AbstractPromptBuyerSerializer.Meta.fields + (
            'size',
        )
