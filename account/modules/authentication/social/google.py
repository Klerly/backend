
from django.conf import settings
from core.exceptions import AuthorizationError
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from account.models import User
import requests
from . import AbstractSocialProvider
from rest_framework.exceptions import ValidationError


class GoogleProvider(AbstractSocialProvider):
    """ Google OAuth provider
    """

    def __init__(self, token):
        self.token = token
        super().__init__()

    def _get_id_token(self):
        """ Get the id token from the authorization code provided

            Returns:
                str: ID token

            Raises:
                AuthorizationError: If the token is invalid
        """

        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': self.token,
                'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
                'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                'redirect_uri': settings.GOOGLE_OAUTH2_REDIRECT_URI,
                'grant_type': 'authorization_code'
            }
        )

        if response.status_code == 200:
            return response.json()['id_token']
        else:
            # print(f'Error: {response.status_code} {response.text}')
            raise AuthorizationError(
                "Invalid token. Token is not a valid Google ID token"
            )

    def _validate_token(self):
        # see: https://developers.google.com/identity/sign-in/web/backend-auth#verify-the-integrity-of-the-id-token
        token = self._get_id_token()
        try:
            decoded_token = id_token.verify_oauth2_token(
                token, google_requests.Request(), settings.GOOGLE_OAUTH2_CLIENT_ID)
        except ValueError:
            raise AuthorizationError(
                "Invalid token. Token is not a valid Google ID token"
            )

        is_expired = self._check_expiry(decoded_token['iat'])
        if is_expired:
            raise AuthorizationError(
                "Token has expired. Please sign in again"
            )
        data = {
            "google_id": decoded_token.get("sub"),
            "email": decoded_token.get("email"),
            "is_active": decoded_token.get("email_verified"),
            "first_name": decoded_token.get("given_name", ""),
            "last_name": decoded_token.get("family_name", ""),
        }
        return User(**data)

    def _get_or_create_user(self, user: User):
        created = False
        try:
            existing_user = User.objects.get(email=user.email)
            if not existing_user.google_id:
                # merges accounts
                existing_user.google_id = user.google_id
                existing_user.save()
            elif not (existing_user.google_id == user.google_id):
                # should never happen
                raise AuthorizationError("Invalid google Id")

            if not existing_user.is_active:
                existing_user.activate()
            user = existing_user

        except User.DoesNotExist:
            user = User.objects.create_user(  # type: ignore
                email=user.email,
                username=user.email,
                password=None,
                google_id=user.google_id,
                first_name=user.first_name,
                last_name=user.last_name,
                is_active=user.is_active
            )
            created = True

        return user, created
