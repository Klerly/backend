from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from jarvis.models import AbstractPromptModel, PromptOutputModel
from rest_framework.exceptions import ValidationError


class Dalle2PromptModel(AbstractPromptModel):
    class ImageSizes(models.TextChoices):
        SMALL = '256x256', _('Small')
        MEDIUM = '512x512', _('Medium')
        LARGE = '1024x1024', _('Large')

    name = AbstractPromptModel.Names.DALLE2
    type = AbstractPromptModel.Types.IMAGE

    class Meta(AbstractPromptModel.Meta):
        verbose_name = _('Dalle2 Prompt')
        verbose_name_plural = _('Dalle2 Prompts')

    def __str__(self):
        return self.heading

    def validate_size(self, size: str):
        if size not in [size for size in self.ImageSizes.values]:
            raise ValidationError("The size you entered is invalid")

    def generate(
        self,
        user,
        size: ImageSizes = ImageSizes.MEDIUM,
        **kwargs
    ) -> PromptOutputModel:

        self.validate_size(size)

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

        output: str = response["data"][0]["url"]  # type: ignore
        model_snapshot = self.__dict__.copy()
        model_snapshot.pop("_state", None)
        model_snapshot["created_at"] = model_snapshot["created_at"].isoformat()
        model_snapshot["updated_at"] = model_snapshot["updated_at"].isoformat()
        outputModel = PromptOutputModel.objects.create(
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
