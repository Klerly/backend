from django.contrib import admin
from completion.models import PromptModel, CompletionModel, DocumentModel

# Register your models here.
admin.site.register(PromptModel)
admin.site.register(CompletionModel)
admin.site.register(DocumentModel)
