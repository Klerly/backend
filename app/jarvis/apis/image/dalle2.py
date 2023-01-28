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
from rest_framework import filters


class Dalle2PromptSellerCreateAPIView(ListCreateAPIView):
    queryset = Dalle2PromptModel.objects.all()
    serializer_class = Dalle2PromptSellerSerializer


class Dalle2PromptSellerRetrieveUpdateDestroyAPIView(
    RetrieveUpdateDestroyAPIView
):
    queryset = Dalle2PromptModel.objects.all()
    serializer_class = Dalle2PromptSellerSerializer

    def get_queryset(self):
        return super().get_queryset().filter(
            user=self.request.user
        )


class Dalle2PromptBuyerListAPIView(ListAPIView):
    queryset = Dalle2PromptModel.objects.active()
    serializer_class = Dalle2PromptBuyerSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'heading',
        'description',
        'template_params',
        'template'
    ]


class Dalle2PromptBuyerRetrieveAPIView(RetrieveAPIView):
    queryset = Dalle2PromptModel.objects.active()
    serializer_class = Dalle2PromptBuyerSerializer
