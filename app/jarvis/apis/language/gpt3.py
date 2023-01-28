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
from rest_framework import filters


class GPT3PromptSellerListCreateAPIView(ListCreateAPIView):
    serializer_class = GPT3PromptSellerSerializer

    def get_queryset(self):
        queryset = GPT3PromptModel.objects.active()
        return queryset.filter(
            user=self.request.user
        )


class GPT3PromptSellerRetrieveUpdateDestroyAPIView(
    RetrieveUpdateDestroyAPIView
):
    serializer_class = GPT3PromptSellerSerializer

    def get_queryset(self):
        queryset = GPT3PromptModel.objects.active()
        return queryset.filter(
            user=self.request.user
        )


class GPT3PromptBuyerListAPIView(ListAPIView):
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
    queryset = GPT3PromptModel.objects.active_for_buyer()
    serializer_class = GPT3PromptBuyerSerializer
