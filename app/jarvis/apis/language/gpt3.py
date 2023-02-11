from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from jarvis.models import (
    GPT3PromptModel,
)
from jarvis.serializers.language.gpt3 import (
    GPT3PromptSellerSerializer,
    GPT3PromptBuyerSerializer
)
from jarvis.apis.common.views.GeneratePromptAPIView import GenerateAPIView
from rest_framework import filters


class GPT3PromptSellerListCreateAPIView(ListCreateAPIView):
    """ List all the prompts created by the seller
        and create a new prompt
    """
    serializer_class = GPT3PromptSellerSerializer

    def get_queryset(self):
        queryset = GPT3PromptModel.objects.active()
        return queryset.filter(
            user=self.request.user
        )


class GPT3PromptSellerRetrieveUpdateDestroyAPIView(
    RetrieveUpdateDestroyAPIView
):
    """ Retrieve, Update, Destroy a prompt"""
    serializer_class = GPT3PromptSellerSerializer

    def get_queryset(self):
        queryset = GPT3PromptModel.objects.active()
        return queryset.filter(
            user=self.request.user
        )


class GPT3PromptBuyerListAPIView(ListAPIView):
    """ List all the prompts available
        to be bought by the buyer
    """
    queryset = GPT3PromptModel.objects.active_for_buyer()
    serializer_class = GPT3PromptBuyerSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'heading',
        'description',
        'template_params',
        'template'
    ]


class GPT3PromptBuyerRetrieveAPIView(RetrieveAPIView):
    """ Retrieve a prompt available
        to be bought by the buyer
    """
    queryset = GPT3PromptModel.objects.active_for_buyer()
    serializer_class = GPT3PromptBuyerSerializer


class GPT3PromptGeneratorAPIView(GenerateAPIView):
    """ Generate a prompt using the GPT3 API"""
    queryset = GPT3PromptModel.objects.active_for_buyer()
    serializer_class = GPT3PromptBuyerSerializer
