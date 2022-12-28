from core.exceptions import AuthorizationError
from account.modules.authentication.social.google import GoogleProvider


class SocialProvider():
    """ Class for handling OAuth provider sign in
    """

    PROVIDERS = {
        'Google': GoogleProvider
    }

    def __init__(self, authorization: str):
        provider, token = self.__extract_token(authorization)
        self.provider = SocialProvider.PROVIDERS[provider](token)

    def login(self):
        """ Log in or sign up with the provider
        """
        return self.provider.login()

    @staticmethod
    def __extract_token(authorization: str):
        """ Extract the token from the authorization header

            Args:
                authorization (str): Authorization header value

            Returns:
                Tuple[str, str]: Provider and token

            Raises:
                AuthorizationError: If the token is invalid
        """
        if not authorization:
            raise AuthorizationError("Invalid token. Token is missing")

        token_l = authorization.split(' ')
        if len(token_l) != 2:
            raise AuthorizationError("Invalid token. Token is invalid")

        provider_key, token = token_l
        if not provider_key in SocialProvider.PROVIDERS:
            raise AuthorizationError(
                "Invalid token. Unsupported provider"
            )

        return provider_key, token
