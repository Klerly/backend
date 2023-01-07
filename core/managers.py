from django.db import models


class BaseModelManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)

    def activate(self, *args, **kwargs):
        self.update(is_active=True)

    def deactivate(self, *args, **kwargs):
        self.update(is_active=False)
