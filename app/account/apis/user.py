
from django.contrib.auth import get_user_model
from core.response import SuccessResponse
from account.serializers.user import (
    UserSerializer
)

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from typing import List, Any
from account.models import User


class UserAPI(APIView):
    permission_classes: List[Any] = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()

    def get(self, request, *args, **kwargs):
        user: User = request.user
        data = self.serializer_class(user).data
        return SuccessResponse(data)
