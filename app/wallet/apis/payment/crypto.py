
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from wallet.models import TransactionModel
from wallet.modules.payment.crypto import CryptoWalletPayment
from core.response import SuccessResponse
from core.exceptions import HttpValidationError
from wallet.serializers.payment import PaymentInitializeSerializer
import hashlib
import hmac
from django.conf import settings
from rest_framework.request import Request
import logging


class CryptoPaymentInitializeAPI(APIView):
    def post(self, request):
        serializer = PaymentInitializeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.data["amount"]  # type: ignore
        data = CryptoWalletPayment(request.user).initialize(amount)

        return SuccessResponse(data)


class CryptoPaymentVerifyAPI(APIView):
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
        data = CryptoWalletPayment(request.user).verify(transaction)
        return SuccessResponse(data)


class CryptoPaymentWebhookAPI(APIView):
    permission_classes = []

    def post(self, request: Request):
        hash_ = hmac.new(settings.LAZERPAY_SECRET_KEY.encode('utf-8'),
                         msg=request.body,
                         digestmod=hashlib.sha256
                         ).hexdigest()
        if hash_ == request.headers['X-Lazerpay-Signature']:
            data = request.data
            if data.get('webhookType') == 'DEPOSIT_TRANSACTION':  # type: ignore
                reference = data["reference"]  # type: ignore
                try:
                    transaction: TransactionModel = TransactionModel.objects.get(
                        reference=reference
                    )
                    CryptoWalletPayment(transaction.user).success(
                        transaction)
                except TransactionModel.DoesNotExist:
                    logging.error(
                        "Transaction not found in webhook. reference:",
                        reference
                    )
                return SuccessResponse({})
            else:
                logging.error(
                    "Unknown event in webhook",
                    request.data.get('webhookType'),  # type: ignore
                    request.data.get('reference')  # type: ignore
                )
                return SuccessResponse({})
        raise PermissionDenied()
