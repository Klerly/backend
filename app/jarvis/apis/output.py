from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)
from jarvis.models import PromptOutputModel
from jarvis.serializers.output import PromptOutputSerializer
from rest_framework import filters


class PromptOutputListAPIView(ListAPIView):
    serializer_class = PromptOutputSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'output',
        'input',
        'type',
        'model_name'
    ]

    def get_queryset(self):
        queryset = PromptOutputModel.objects.active()
        return queryset.filter(
            user=self.request.user
        )


class PromptOutputRetrieveAPIView(RetrieveAPIView):
    serializer_class = PromptOutputSerializer

    def get_queryset(self):
        queryset = PromptOutputModel.objects.active()
        return queryset.filter(
            user=self.request.user
        )
