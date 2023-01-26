from django.db import models


class BaseModelManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)

    def restore(self, *args, **kwargs):
        self.update(is_active=True)

    def delete(self, *args, **kwargs):
        self.update(is_active=False)
    
    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

