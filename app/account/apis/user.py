
from django.contrib.auth import get_user_model
from core.response import SuccessResponse
from account.serializers.user import (
    UserSerializer,
    SellerSerializer,
    PublicSellerSerializer
)

from rest_framework.views import APIView
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveAPIView,
    ListCreateAPIView,
    RetrieveUpdateAPIView
)
from rest_framework.permissions import IsAuthenticated
from typing import List, Any
from account.models import User, Seller
from rest_framework import filters
from django.core.exceptions import ObjectDoesNotExist


class UserAPI(APIView):
    permission_classes: List[Any] = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()

    def get(self, request, *args, **kwargs):
        user: User = request.user
        data = self.serializer_class(user).data
        return SuccessResponse(data)


class PublicSellerListAPI(ListCreateAPIView):
    """ List all sellers 

        This API is public and does not require authentication.
        It should be used to list all sellers in the system.
    """
    permission_classes: List[Any] = []
    serializer_class = PublicSellerSerializer
    queryset = Seller.objects.active()
    filter_backends = [filters.SearchFilter]
    search_fields = ['handle', 'name']


class PublicSellerRetrieveAPI(RetrieveAPIView):
    """ Retrieve a seller
    
        This API is public and does not require authentication.
        It should be used to retrieve a seller in the system.
    """
    permission_classes: List[Any] = []
    serializer_class = PublicSellerSerializer
    queryset = Seller.objects.active()
    lookup_field = "handle"


class SellerCreateAPI(CreateAPIView):
    """ Create a seller profile
    
        This API is private and requires authentication.
        It should be used to create a seller profile.
    """
    serializer_class = SellerSerializer


class SellerRetrieveUpdateAPI(RetrieveUpdateAPIView):
    """ Retrieve or update a seller profile
    
        This API is private and requires authentication.
        It should be used to retrieve or update a seller profile.
    """
    serializer_class = SellerSerializer
    queryset = Seller.objects.all()

    def get_object(self):
        self.lookup_field = "user"
        self.kwargs[self.lookup_field] = self.request.user
        return super().get_object()
