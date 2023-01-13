from rest_framework.exceptions import ValidationError
from django.conf import settings
from rest_framework import status


class HttpValidationError(ValidationError):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail):
        if not isinstance(detail, dict):
            if isinstance(detail, str):
                detail = [detail]
            detail = {"non_field_errors": detail}

        if settings.DEBUG:
            assert isinstance(detail, dict)
            for key, value in detail.items():
                assert isinstance(value, list)
                for item in value:
                    assert isinstance(item, str)

        super().__init__(detail=detail)


class AuthorizationError(HttpValidationError):
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self, detail):
        super().__init__(detail)
