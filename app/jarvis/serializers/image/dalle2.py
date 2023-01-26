from rest_framework import serializers
from jarvis.models import (
    Dalle2PromptModel,
    Dalle2PromptOutputModel
)
from jarvis.serializers.abstract import AbstractPromptSellerSerializer


class Dalle2PromptSellerSerializer(AbstractPromptSellerSerializer):
    class Meta(AbstractPromptSellerSerializer.Meta):
        model = Dalle2PromptModel
        output_model = Dalle2PromptOutputModel
        fields = AbstractPromptSellerSerializer.Meta.fields
