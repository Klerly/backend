from django.db import models
from .managers import BaseModelManager

# Create your models here.


class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BaseModelManager()

    class Meta:
        abstract = True
        ordering = ('-created_at',)

    def restore(self, *args, **kwargs):
        self.is_active = True
        self.save()

    def delete(self, *args, **kwargs):
        self.is_active = False
        self.save()
