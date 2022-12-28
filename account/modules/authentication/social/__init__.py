import abc
import datetime as dt
from typing import Tuple
from django.conf import settings
from account.models import User


class AbstractSocialProvider(abc.ABC):
    """ Abstract class for OAuth providers
    """

    @staticmethod
    def _check_expiry(milliseconds: int) -> bool:
        """ Check if oauth tokens have expired 
            x minutes after they are issued

            Args: iat - issued at timestamp (in utc)

            Returns: True if it is expired else False

        """
        time_limit = settings.OAUTH_TOKEN_TTL_MINS or 1
        now = dt.datetime.utcnow()
        expiration_time = dt.datetime.fromtimestamp(
            milliseconds) + dt.timedelta(minutes=time_limit)

        return now > expiration_time

    @abc.abstractmethod
    def _validate_token(self) -> User:
        """ Validate the token provided

            Returns:
                 User : user object

            Raises:
                HttpValidationError: If the token is invalid

            Note:
                This method must be implemented by the child class
        """
        pass

    @abc.abstractmethod
    def _get_or_create_user(self, user:  User) -> Tuple[User, bool]:
        """ Get or create a user from the data provided

            Args:
                user ( User ): Unsaved user object

            Returns:
                Tuple[User, bool]: User object and whether the user was created

            Raises:
                HttpValidationError: If the data is invalid

            Note:
                This method must be implemented by the child class
        """
        pass

    def login(self):
        """ Login or sign up a user

            Returns:
                Tuple[User, bool]: User object and whether the user was created

        """
        user = self._validate_token()
        return self._get_or_create_user(user)
