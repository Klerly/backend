from django.conf import settings
from paystackapi.transaction import Transaction as T
from account.models import User
from core.modules.payment.fiat.paystack import ResponseType
from core.modules.payment import AbstractPayment
from wallet.models import TransactionModel


class Paystack(AbstractPayment):
    def __init__(self, user: User):
        self.user = user

    @staticmethod
    def _convert_to_kobo(amount: int):
        amount = Paystack.validate_integer_amount(amount)
        return amount * 100

    @staticmethod
    def _handle_response(response):
        if response["status"] is not True:
            raise Exception(response["message"])
        return response["data"]

    def initialize(self, amount: int):
        transaction = TransactionModel(
            user=self.user,
            amount=amount,
            status=TransactionModel.Status.PENDING
        )
        transaction.make_reference()
        transaction.save()

        response = T.initialize(
            email=self.user.email,
            amount=self._convert_to_kobo(amount),
            reference=transaction.reference,
            callback_url=settings.PAYSTACK_CALLBACK_URL
        )

        data: ResponseType.InitializationResponse
        data = self._handle_response(response)
        return data

    def verify(self, reference: str):
        response = T.verify(reference=reference)
        data: ResponseType.ChargeResponse
        data = self._handle_response(response)
        status = True if data["status"] == "success" else False
        return status, data

    def withdraw(self, amount: int) -> bool:
        return False

    def charge(self,
               amount: int,
               authorization_code: str,
               transaction: TransactionModel
               ):
        Paystack.validate_integer_amount(amount)

        response = T.charge(
            email=self.user.email,
            amount=self._convert_to_kobo(amount),
            authorization_code=authorization_code,
            reference=transaction.reference,
        )

        data: ResponseType.ChargeResponse
        data = self._handle_response(response)
        status = True if data["status"] == "success" else False
        return status, data
