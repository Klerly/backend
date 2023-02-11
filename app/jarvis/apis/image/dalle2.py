from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from jarvis.models import (
    Dalle2PromptModel,
)
from jarvis.serializers.image.dalle2 import (
    Dalle2PromptSellerSerializer,
    Dalle2PromptBuyerSerializer
)

from jarvis.apis.common.views.GeneratePromptAPIView import GenerateAPIView
from rest_framework import filters


class Dalle2PromptSellerListCreateAPIView(ListCreateAPIView):
    serializer_class = Dalle2PromptSellerSerializer

    def get_queryset(self):
        queryset = Dalle2PromptModel.objects.active()
        return queryset.filter(
            user=self.request.user
        )


class Dalle2PromptSellerRetrieveUpdateDestroyAPIView(
    RetrieveUpdateDestroyAPIView
):
    serializer_class = Dalle2PromptSellerSerializer

    def get_queryset(self):
        queryset = Dalle2PromptModel.objects.active()
        return queryset.filter(
            user=self.request.user
        )


class Dalle2PromptBuyerListAPIView(ListAPIView):
    queryset = Dalle2PromptModel.objects.active_for_buyer()
    serializer_class = Dalle2PromptBuyerSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'heading',
        'description',
        'template_params',
        'template'
    ]


class Dalle2PromptBuyerRetrieveAPIView(RetrieveAPIView):
    queryset = Dalle2PromptModel.objects.active_for_buyer()
    serializer_class = Dalle2PromptBuyerSerializer


class Dalle2PromptGeneratorAPIView(GenerateAPIView):
    """ Generate a prompt using the GPT3 API"""
    queryset = Dalle2PromptModel.objects.active_for_buyer()
    serializer_class = Dalle2PromptBuyerSerializer
