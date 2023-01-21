from account.models import User
from wallet.models import WalletModel, CardModel, TransactionModel
from core.modules.payment.fiat.paystack import Paystack, ResponseType as PaystackResponseType


class FiatWalletPayment:
    def __init__(self, user: User):
        self.user = user
        self.provider = self._get_provider(user)

    def _get_provider(self, user: User):
        return Paystack(user)

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
            message = "We have not received your payment"

        return {
            "status": False,
            "message": message
        }

    def initialize(self, amount: int):
        amount = self.provider.validate_integer_amount(amount)
        data = self.provider.initialize(amount)
        return data

    def verify(self, transaction: TransactionModel):
        status, data = self.provider.verify(transaction.reference)
        if status == True:
            return self._success(transaction, data)
        else:
            return self._failed(transaction, data)

    def withdraw(self, amount: int) -> bool:
        return self.provider.withdraw(amount)

    def charge(self, card: CardModel, amount: int):
        amount = self.provider.validate_integer_amount(amount)
        transaction: TransactionModel = TransactionModel(
            user=self.user,
            amount=amount,
            status=TransactionModel.Status.PENDING
        )
        transaction.make_reference()
        transaction.save()

        status, data = self.provider.charge(
            amount,
            card.authorization_code,
            transaction
        )

        if status == True:
            return self._success(transaction, data)
        else:
            return self._failed(transaction, data)

    def success(self, transaction: TransactionModel, data: PaystackResponseType.ChargeResponse):
        return self._success(transaction, data)

    def failed(self, transaction: TransactionModel, data: PaystackResponseType.ChargeResponse):
        return self._failed(transaction, data)
