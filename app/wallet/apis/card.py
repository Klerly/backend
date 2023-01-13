from wallet.serializers.card import CardSerializer
from wallet.models import CardModel
from rest_framework import generics


class CardListAPI(generics.ListAPIView):
    serializer_class = CardSerializer

    def get_queryset(self):
        return CardModel.objects.filter(user=self.request.user)


class CardRetrieveUpdateDestroyAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CardSerializer

    def get_queryset(self):
        return CardModel.objects.filter(user=self.request.user)
