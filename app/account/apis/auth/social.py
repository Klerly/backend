from rest_framework.views import APIView
from typing import List, Any
from account.modules.authentication.social.base import SocialProvider
from rest_framework import status
from core.response import SuccessResponse
from django.http import HttpRequest


class SocialSignInAPI(APIView):
    """ Log in or sign up with Google
    """
    permission_classes: List[Any] = []

    def post(self, request: HttpRequest):
        token = request.headers.get('Authorization', "")
        user, created = SocialProvider(token).login()
        status_code = status.HTTP_200_OK if not created else status.HTTP_201_CREATED
        data = user.login()
        return SuccessResponse(data, status=status_code)
