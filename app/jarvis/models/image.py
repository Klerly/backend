from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from jarvis.models import AbstractPromptModel, AbstractPromptOutputModel


class Dalle2PromptModel(AbstractPromptModel):
    class ImageSizes(models.TextChoices):
        SMALL = '256x256', _('Small')
        MEDIUM = '512x512', _('Medium')
        LARGE = '1024x1024', _('Large')

    type = AbstractPromptModel.Types.IMAGE
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('User'),
        related_name='dalle2_prompts'
    )

    class Meta:
        verbose_name = _('Dalle2 Prompt')
        verbose_name_plural = _('Dalle2 Prompts')
        ordering = ('-created_at',)

    def __str__(self):
        return self.heading

    def generate(
        self,
        size: ImageSizes = ImageSizes.MEDIUM,
        **kwargs
    ):
        # if "size" not in kwargs or kwargs["size"] not in self.ImageSizes.values:
        #     raise ValueError(
        #         'The "size" parameter is missing or invalid. Ensure that the input has the format {{ "size": "256x256" }}'
        #     )

        import openai
        openai.api_key = settings.OPENAI_API_KEY
        prompt = self.get_prompt(**kwargs)
        response = openai.Image.create(
            size=size,
            user=str(self.user.id),
            prompt=prompt,
            response_format="url",  # or "b64_json"
            n=1
        )

        output = response["data"][0]["url"]  # type: ignore
        model_snapshot = self.__dict__.copy()
        model_snapshot.pop("_state", None)
        model_snapshot["created_at"] = model_snapshot["created_at"].isoformat()
        model_snapshot["updated_at"] = model_snapshot["updated_at"].isoformat()
        Dalle2PromptOutputModel.objects.create(
            uid=output,  # type: ignore
            user=self.user,
            model_input=prompt,
            input=kwargs or None,
            output=output,
            model=self,
            cost=0.0,
            model_snapshot=model_snapshot
        )

        return output


class Dalle2PromptOutputModel(AbstractPromptOutputModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('User'),
        related_name='dalle2_prompt_outputs'
    )
    model = models.ForeignKey(
        Dalle2PromptModel,
        on_delete=models.DO_NOTHING,
        related_name='dalle2_prompt_outputs'
    )
    type = AbstractPromptModel.Types.IMAGE

    class Meta:
        verbose_name = _('Dalle2 Output')
        verbose_name_plural = _('Dalle2 Outputs')
        ordering = ('-created_at',)
