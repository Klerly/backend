from wallet.serializers.transaction import TransactionSerializer
from wallet.models import TransactionModel
from rest_framework import generics


class TransactionListAPI(generics.ListAPIView):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return TransactionModel.objects.filter(user=self.request.user)


class TransactionRetrieveAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return TransactionModel.objects.filter(user=self.request.user)
