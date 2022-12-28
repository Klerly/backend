from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


class SuccessResponse(Response):
    def __init__(self, data=None, status=status.HTTP_200_OK):
        if isinstance(data, str):
            data = {"message": [data]}

        if settings.DEBUG:
            assert isinstance(data, dict)
        super().__init__(status=status, data=data)
