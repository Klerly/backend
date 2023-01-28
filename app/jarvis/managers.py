from core.managers import BaseModelManager


class PromptModelManager(BaseModelManager):
    def active_for_buyer(self, *args, **kwargs):
        return super().active().filter(
            *args,
            **kwargs,
            user__seller_profile__is_active=True,
            user__is_active=True,
            user__is_verified=True
        )
