from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from jarvis.models import AbstractPromptModel, PromptOutputModel


class GPT3PromptModel(AbstractPromptModel):
    class Models(models.TextChoices):
        DAVINCI_003 = 'text-davinci-003', _('Davinci')
        CURIE_001 = 'text-curie-001', _('Curie')
        BABBAGE_001 = 'text-babbage-001', _('Babbage')
        ADA_001 = 'text-ada-001', _('Ada')

    name = AbstractPromptModel.Names.GPT3
    type = AbstractPromptModel.Types.TEXT

    model = models.CharField(
        max_length=255,
        choices=Models.choices,
        default=Models.DAVINCI_003
    )
    max_tokens = models.IntegerField(
        default=2048
    )
    top_p = models.FloatField(
        default=1.0
    )
    temparature = models.FloatField(
        default=0.9
    )
    frequency_penalty = models.FloatField(
        default=0.0
    )
    presence_penalty = models.FloatField(
        default=0.0
    )
    suffix = models.CharField(
        max_length=255,
        default=""
    )

    class Meta(AbstractPromptModel.Meta):
        verbose_name = _('GPT3 Prompt')
        verbose_name_plural = _('GPT3 Prompts')

    def __str__(self):
        return self.heading

    def _validate_model(self):
        if self.model not in [model for model in self.Models.values]:
            raise ValueError("The model you entered is invalid")

    def save(self, *args, **kwargs):
        self._validate_model()
        return super().save(*args, **kwargs)

    def generate(self, user, **kwargs) -> PromptOutputModel:
        import openai
        openai.api_key = settings.OPENAI_API_KEY
        prompt = self.get_prompt(**kwargs)

        response = openai.Completion.create(
            model=self.model,
            temperature=self.temparature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            user=str(self.user.id),
            prompt=prompt,
            echo=False,
            stream=False,
        )

        output = response["choices"][0]["text"]  # type: ignore
        model_snapshot = self.__dict__.copy()
        model_snapshot.pop("_state", None)
        model_snapshot["created_at"] = model_snapshot["created_at"].isoformat()
        model_snapshot["updated_at"] = model_snapshot["updated_at"].isoformat()
        outputModel = PromptOutputModel.objects.create(
            uid=response["id"],  # type: ignore
            user=user,
            input=kwargs or None,
            output=output,
            cost=0.0,
            type=self.type,
            model_name=self.name,
            model_input=prompt,
            model_user=self.user,
            model_snapshot=model_snapshot
        )

        return outputModel
