
from rest_framework.views import APIView
from wallet.models import TransactionModel, CardModel
from wallet.modules.payment import Payment
from core.response import SuccessResponse
from core.exceptions import HttpValidationError
from wallet.serializers.payment import PaymentInitializeSerializer, PaymentChargeSerializer


class PaymentInitializeAPI(APIView):
    def post(self, request):
        serializer = PaymentInitializeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.data["amount"]  # type: ignore
        data = Payment(request.user).initialize(amount)

        return SuccessResponse(data)


class PaymentVerifyAPI(APIView):
    def get(self, request, reference: str):
        try:
            transaction: TransactionModel = TransactionModel.objects.get(
                user=request.user,
                reference=reference
            )
        except TransactionModel.DoesNotExist:
            raise HttpValidationError(
                "Transaction not found"
            )
        if transaction.status != TransactionModel.Status.SUCCESS:
            raise HttpValidationError(
                "Transaction already completed"
            )
        data = Payment(request.user).verify(transaction)
        return SuccessResponse(data)


class PaymentChargeAPI(APIView):
    def post(self, request):
        serializer = PaymentChargeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.data["amount"]  # type: ignore
        signature = serializer.validated_data["signature"]  # type: ignore

        try:
            card: CardModel = CardModel.objects.get(
                user=request.user,
                signature=signature
            )
        except CardModel.DoesNotExist:
            raise HttpValidationError(
                "Card not found"
            )

        data = Payment(request.user).charge(card, amount)
        return SuccessResponse(data)
