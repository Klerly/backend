from jarvis.models import (
    GPT3PromptModel
)
from jarvis.serializers.abstract import (
    AbstractPromptSellerSerializer,
    AbstractPromptBuyerSerializer
)


class GPT3PromptSellerSerializer(AbstractPromptSellerSerializer):
    class Meta(AbstractPromptSellerSerializer.Meta):
        model = GPT3PromptModel
        fields = AbstractPromptSellerSerializer.Meta.fields + (
            'model',
            'max_tokens',
            'top_p',
            'temparature',
            'frequency_penalty',
            'presence_penalty',
            'suffix',
        )


class GPT3PromptBuyerSerializer(AbstractPromptBuyerSerializer):
    class Meta(AbstractPromptBuyerSerializer.Meta):
        model = GPT3PromptModel
