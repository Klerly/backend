from django.db import models
from core.models import BaseModel
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class PromptModel(BaseModel):
    heading = models.CharField(max_length=255)
    image = models.URLField(max_length=255)
    description = models.TextField()
    prompt = models.TextField()  # actual secret prompt

    class Meta:
        verbose_name = _('Prompt')
        verbose_name_plural = _('Prompts')
        ordering = ('-created_at',)

    def __str__(self):
        return self.heading

    def delete(self, *args, **kwargs):
        return self.objects.deactivate()


class CompletionModel(models.Model):
    uid = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('User'),
        related_name='completions'
    )
    input = models.TextField()
    output = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Completion')
        verbose_name_plural = _('Completions')
        ordering = ('-created_at',)

    def __str__(self):
        return "{} - {}".format(self.user, self.uid)

    def delete(self, *args, **kwargs):
        return None


class DocumentModel(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('User'),
        related_name='documents'
    )
    prompt = models.ForeignKey(
        PromptModel,
        on_delete=models.CASCADE,
        verbose_name=_('Prompt'),
        related_name='documents'
    )
    name = models.CharField(max_length=255)
    text = models.TextField()

    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')
        ordering = ('-updated_at',)

    def __str__(self):
        return "{} - {}".format(self.user, self.name)

    def complete(self, new_text: str):
        import openai
        openai.api_key = settings.OPENAI_API_KEY
        prompt = self.prompt.prompt + new_text
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0,
            max_tokens=3000,
            top_p=1.0,
            stream=False,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        res_text = response["choices"][0]["text"]  # type: ignore

        CompletionModel.objects.create(
            uid=response["id"],  # type: ignore
            user=self.user,
            input=prompt,
            output=res_text
        )

        return res_text
