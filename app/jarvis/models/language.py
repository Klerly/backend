from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from jarvis.models import AbstractPromptModel, AbstractPromptOutputModel


class GPT3PromptModel(AbstractPromptModel):
    class Models(models.TextChoices):
        DAVINCI_003 = 'text-davinci-003', _('Davinci')
        CURIE_001 = 'text-curie-001', _('Curie')
        BABBAGE_001 = 'text-babbage-001', _('Babbage')
        ADA_001 = 'text-ada-001', _('Ada')

    type = AbstractPromptModel.Types.TEXT
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('User'),
        related_name='language_prompts'
    )
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

    class Meta:
        verbose_name = _('GPT3 Prompt')
        verbose_name_plural = _('GPT3 Prompts')
        ordering = ('-created_at',)

    def __str__(self):
        return self.heading

    def _validate_model(self):
        if self.model not in [model for model in self.Models.values]:
            raise ValueError("The model you entered is invalid")

    def save(self, *args, **kwargs):
        self._validate_model()
        return super().save(*args, **kwargs)

    def complete(self, **kwargs):
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
        GPT3PromptOutputModel.objects.create(
            uid=response["id"],  # type: ignore
            user=self.user,
            model_input=prompt,
            input=kwargs or None,
            output=output,
            model=self,
            cost=0.0,
            model_snapshot=model_snapshot
        )

        return output


class GPT3PromptOutputModel(AbstractPromptOutputModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('User'),
        related_name='gpt3_prompt_outputs'
    )
    model = models.ForeignKey(
        GPT3PromptModel,
        on_delete=models.DO_NOTHING,
        related_name='gpt3_prompt_outputs'
    )

    type = AbstractPromptModel.Types.TEXT

    class Meta:
        verbose_name = _('GPT3 Output')
        verbose_name_plural = _('GPT3 Outputs')
        ordering = ('-created_at',)
