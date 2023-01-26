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

    def validate_model(self, value):
        """ Validate the model field

        Args:
            value (str): The model

        Raises:
            serializers.ValidationError: If the model is not valid

        Returns:
            str: The model
        """
        if value not in GPT3PromptModel.Models.values:
            raise serializers.ValidationError(
                "The openai model that was entered is invalid"
            )

        return value
