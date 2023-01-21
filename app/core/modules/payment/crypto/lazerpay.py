from account.models import User
from wallet.models import TransactionModel
from core.modules.payment import AbstractPayment
from django.conf import settings
from requests.models import Response
import requests


class LazerPay(AbstractPayment):
    class URLS:
        BASE = "https://api.lazerpay.engineering/api/v1/"
        INITIIALIZE = BASE + "/transaction/initialize"
        VERIFY = BASE + "/transaction/verify"
        TRANSFER = BASE + "/transfer"

    def __init__(self, user: User):
        self.user = user
        self.coin = "USDT"

    def _make_request(self, method: str, url: str, payload: dict = {}):
        headers = {
            'x-api-key': settings.LAZERPAY_PUBLIC_KEY,
            "Authorization": "Bearer {token}".format(token=settings.LAZERPAY_SECRET_KEY),
        }
        response = requests.request(method, url, headers=headers, data=payload)
        return self._handle_response(response)

    @staticmethod
    def _handle_response(response: Response):
        if response.status_code == 200 or response.status_code == 201:
            if response.json()["status"] == "success":
                return response.json()["data"]
        raise Exception(response.json()["message"])

    def validate_blockchain_address(self, address: str):
        if address.startswith("0x") and len(address) == 42:
            return True
        raise Exception("Invalid blockchain address")

    def initialize(self, amount: int):
        amount = self.validate_integer_amount(amount)
        transaction = TransactionModel(
            user=self.user,
            amount=amount,
            status=TransactionModel.Status.PENDING
        )
        transaction.make_reference()
        transaction.save()

        payload = {
            "customer_name": "{user.first_name} {user.last_name}".format(user=self.user),
            "customer_email": self.user.email,
            "coin": self.coin,
            "currency": "USD",
            "amount": transaction.amount
        }

        json_res = self._make_request(
            "post",
            self.URLS.INITIIALIZE,
            payload
        )

        return json_res

    def verify(self, reference: str):
        url = "{url}/{reference}".format(url=self.URLS.VERIFY,
                                         reference=reference
                                         )
        json_res = self._make_request("get", url)

        network = "testnet" if settings.DEBUG else "mainnet"
        if json_res["status"] == "confirmed":
            if json_res["actualAmount"] == json_res["amountPaid"]:
                if json_res["network"] == network:
                    return True
        return False

    def withdraw(self, amount: int):
        address = self.user.wallet.address  # type: ignore
        self.validate_blockchain_address(
            address
        )
        amount = self.validate_integer_amount(amount)

        transaction = TransactionModel(
            user=self.user,
            amount=amount,
            status=TransactionModel.Status.PENDING,
            type=TransactionModel.Type.WITHDRAWAL
        )
        transaction.make_reference()
        transaction.save()

        payload = {
            "reference": transaction.reference,
            "amount": amount,
            "coin": self.coin,
            "recepient": address,
            "blockchain": "Binance Smart Chain"
        }
        self._make_request("post", self.URLS.TRANSFER, payload)

        transaction.status = TransactionModel.Status.SUCCESS
        transaction.save()

        return True
