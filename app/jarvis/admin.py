from jarvis.models import (
    GPT3PromptModel,
    Dalle2PromptModel,
    PromptOutputModel,
)
from django.contrib import admin

# Register your models here.
admin.site.register(GPT3PromptModel)
admin.site.register(Dalle2PromptModel)
admin.site.register(PromptOutputModel)
