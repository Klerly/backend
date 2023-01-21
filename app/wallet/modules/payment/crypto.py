from account.models import User
from wallet.models import WalletModel, TransactionModel
from core.modules.payment.crypto.lazerpay import LazerPay


class CryptoWalletPayment:
    def __init__(self, user: User):
        self.user = user
        self.provider = self._get_provider(user)

    def _get_provider(self, user: User):
        return LazerPay(user)

    def _success(self, transaction: TransactionModel):
        if transaction.status != TransactionModel.Status.SUCCESS:
            transaction.status = TransactionModel.Status.SUCCESS
            transaction.save()

            wallet: WalletModel = self.user.wallet  # type: ignore
            wallet.fund(transaction.amount)
        return {
            "status": True,
            "message": "Payment successful"
        }

    def _failed(self, transaction: TransactionModel):
        if transaction.status != TransactionModel.Status.SUCCESS:
            transaction.status = TransactionModel.Status.PENDING
            transaction.save()
        # if "gateway_response" in data:
        #     message = data["gateway_response"]
        # else:
        message = "We have not received your payment"

        return {
            "status": False,
            "message": message
        }

    def initialize(self, amount: int):
        amount = self.provider.validate_integer_amount(amount)
        return self.provider.initialize(amount)

    def verify(self, transaction: TransactionModel):
        status = self.provider.verify(transaction.reference)
        if status == True:
            return self._success(transaction)
        else:
            return self._failed(transaction)

    def transfer(self, amount: int) -> bool:
        return self.provider.withdraw(amount)

    def success(self, transaction: TransactionModel):
        return self._success(transaction)

    def failed(self, transaction: TransactionModel):
        return self._failed(transaction)
