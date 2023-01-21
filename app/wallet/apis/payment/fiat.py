
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from wallet.models import TransactionModel, CardModel
from wallet.modules.payment.fiat import FiatWalletPayment
from core.response import SuccessResponse
from core.exceptions import HttpValidationError
from wallet.serializers.payment import PaymentInitializeSerializer, PaymentChargeSerializer
import hashlib
import hmac
from django.conf import settings
from rest_framework.request import Request
import logging


class PaymentInitializeAPI(APIView):
    def post(self, request):
        serializer = PaymentInitializeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.data["amount"]  # type: ignore
        data = FiatWalletPayment(request.user).initialize(amount)

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
        if transaction.status == TransactionModel.Status.SUCCESS:
            raise HttpValidationError(
                "Transaction already completed"
            )
        data = FiatWalletPayment(request.user).verify(transaction)
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

        data = FiatWalletPayment(request.user).charge(card, amount)
        return SuccessResponse(data)


class PaymentWebhookAPI(APIView):
    permission_classes = []

    def post(self, request: Request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        if ip_address in settings.PAYSTACK_WHITELISTED_IPS:
            hash_ = hmac.new(settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
                             msg=request.body,
                             digestmod=hashlib.sha512
                             ).hexdigest()
            if hash_ == request.headers['X-Paystack-Signature']:
                if request.data.get('event') == 'charge.success':  # type: ignore
                    data = request.data.get('data')  # type: ignore
                    if data["status"] == "success":  # type: ignore
                        reference = data["reference"]  # type: ignore
                        try:
                            transaction: TransactionModel = TransactionModel.objects.get(
                                reference=reference
                            )
                            FiatWalletPayment(transaction.user).success(
                                transaction, data)  # type: ignore
                        except TransactionModel.DoesNotExist:
                            logging.error(
                                "Transaction not found in webhook. reference",
                                reference
                            )
                    return SuccessResponse({})
                else:
                    logging.error(
                        "Unknown event in webhook",
                        request.data.get('event'),  # type: ignore
                        request.data.get('data')["reference"]  # type: ignore
                    )
                    return SuccessResponse({})
        raise PermissionDenied()
