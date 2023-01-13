
from django.conf import settings
from paystackapi.transaction import Transaction as T
from account.models import User
from wallet.modules.payment.paystack import ResponseType


class Paystack:
    def __init__(self, user: User):
        self.user = user
        self.api_key = settings.PAYSTACK_SECRET_KEY

    @staticmethod
    def _convert_to_kobo(amount: int):
        from wallet.modules.payment import Payment
        amount = Payment.validate_integer_amount(amount)
        return amount * 100

    @staticmethod
    def _handle_response(response):
        if response["status"] is not True:
            raise Exception(response["message"])
        return response["data"]

    def initialize(self, amount: int):
        response = T.initialize(
            email=self.user.email,
            amount=self._convert_to_kobo(amount),
            callback_url=settings.PAYSTACK_CALLBACK_URL
        )

        data: ResponseType.InitializationResponse
        data = self._handle_response(response)
        return data

    def charge(self, amount: int, authorization_code: str):
        response = T.charge(
            email=self.user.email,
            amount=self._convert_to_kobo(amount),
            authorization_code=authorization_code
        )

        data: ResponseType.ChargeResponse
        data = self._handle_response(response)
        data["paid"] = True if data["status"] == "success" else False
        return data

    def verify(self, reference: str):
        response = T.verify(reference=reference)
        data: ResponseType.ChargeResponse
        data = self._handle_response(response)
        data["paid"] = True if data["status"] == "success" else False

        return data
