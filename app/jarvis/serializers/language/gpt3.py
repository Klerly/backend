from rest_framework import serializers
from jarvis.models import (
    GPT3PromptModel,
    GPT3PromptOutputModel
)
from jarvis.serializers.abstract import AbstractPromptSellerSerializer


class GPT3PromptSellerSerializer(AbstractPromptSellerSerializer):
    class Meta(AbstractPromptSellerSerializer.Meta):
        model = GPT3PromptModel
        output_model = GPT3PromptOutputModel
        fields = AbstractPromptSellerSerializer.Meta.fields + (
            'model',
            'max_tokens',
            'top_p',
            'temparature',
            'frequency_penalty',
            'presence_penalty',
            'suffix',
        )
