from rest_framework import authentication, exceptions
from django.utils.translation import gettext_lazy as _


class CustomTokenAuthentication(authentication.TokenAuthentication):
    def get_model(self):
        if self.model is not None:
            return self.model
        from account.models import TokenAuthenticationProxyModel
        return TokenAuthenticationProxyModel

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(
                _('User inactive or deleted.'))
        if token.has_expired():
            raise exceptions.AuthenticationFailed('Token has expired')
        return (token.user, token)
