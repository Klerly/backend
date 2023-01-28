from jarvis.models import (
    GPT3PromptModel,
    GPT3PromptOutputModel
)
from typing import Union
from jarvis.serializers.abstract import (
    AbstractPromptSellerSerializer,
    AbstractPromptBuyerSerializer
)


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


class GPT3PromptBuyerSerializer(AbstractPromptBuyerSerializer):
    class Meta(AbstractPromptBuyerSerializer.Meta):
        model = GPT3PromptModel

    def generate(self) -> str:
        instance: Union[GPT3PromptModel,
                        AbstractPromptModel] = self.instance  # type: ignore
        return instance.generate(**self.validated_data)  # type: ignore
