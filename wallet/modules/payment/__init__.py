from account.models import User
from wallet.models import WalletModel, CardModel, TransactionModel
from wallet.modules.payment.paystack import ResponseType as PaystackResponseType
from wallet.modules.payment.paystack import Paystack
from decimal import Decimal


class Payment:
    def __init__(self, user: User):
        self.user = user
        self.provider = self._get_provider(user)

    def _get_provider(self, user: User):
        return Paystack(self.user)

    def _add_card(self, data: PaystackResponseType.ChargeResponse):
        if data["channel"] == "card":
            if data["authorization"]["reusable"] is True:
                if not CardModel.objects.filter(
                        user=self.user,
                        signature=data["authorization"]["signature"]
                     ).exists():
                    CardModel.objects.create(
                        user=self.user,
                        data=data["authorization"]
                    )

    def _success(self, transaction: TransactionModel, data: PaystackResponseType.ChargeResponse):
        if transaction.status != TransactionModel.Status.SUCCESS:
            self._add_card(data)

            transaction.status = TransactionModel.Status.SUCCESS
            transaction.save()

            wallet: WalletModel = self.user.wallet  # type: ignore
            wallet.fund(transaction.amount)
        return {
            "status": True,
            "message": "Payment successful"
        }

    def _failed(self, transaction: TransactionModel, data: PaystackResponseType.ChargeResponse):
        if transaction.status != TransactionModel.Status.SUCCESS:
            transaction.status = TransactionModel.Status.FAILED
            transaction.save()

        if "gateway_response" in data:
            message = data["gateway_response"]
        else:
            message = "Payment failed"

        return {
            "status": False,
            "message": message
        }

    @staticmethod
    def validate_integer_amount(amount: int):
        # when testing, ensure that the integer test is called first
        if type(amount) != int:
            raise ValueError("Amount must be an integer")
        if amount % 1 != 0:
            raise ValueError("Amount must be an integer")
        if amount < 0:
            raise ValueError("Amount must be a positive number")
        return amount

    @staticmethod
    def validate_decimal_amount(amount: Decimal):
        if amount < 0:
            raise ValueError("Amount must be a positive number")
        return amount

    def initialize(self, amount: int):
        amount = self.validate_integer_amount(amount)
        data = self.provider.initialize(amount)
        TransactionModel.objects.create(
            user=self.user,
            amount=amount,
            reference=data["reference"],
            status=TransactionModel.Status.PENDING
        )
        return data

    def verify(self, transaction: TransactionModel):
        data = self.provider.verify(transaction.reference)
        if data["paid"] == True:
            return self._success(transaction, data)
        else:
            return self._failed(transaction, data)

    def charge(self, card: CardModel, amount: int):
        amount = self.validate_integer_amount(amount)
        data = self.provider.charge(amount, card.authorization_code)
        transaction: TransactionModel = TransactionModel(
            user=self.user,
            amount=amount,
            reference=data["reference"],
            status=TransactionModel.Status.PENDING
        )
        if data["paid"] == True:
            return self._success(transaction, data)
        else:
            return self._failed(transaction, data)
