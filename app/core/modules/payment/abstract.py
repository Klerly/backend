
import abc
from decimal import Decimal
from wallet.models import TransactionModel
from typing import Optional, Tuple


class AbstractPayment(abc.ABC):
    """
    Abstract base class for payments
    """

    @classmethod
    def validate_integer_amount(cls, amount: int):
        # when testing, ensure that the integer test is called first
        if type(amount) != int:
            raise ValueError("Amount must be an integer")
        if amount % 1 != 0:
            raise ValueError("Amount must be an integer")
        if amount < 0:
            raise ValueError("Amount must be a positive number")
        return amount

    @classmethod
    def validate_decimal_amount(cls, amount: Decimal):
        if amount < 0:
            raise ValueError("Amount must be a positive number")
        return amount

    @abc.abstractmethod
    def initialize(self, amount: int) -> dict:
        """
        Initialize payment

        Args:
            amount(int): Integer amount to initialize payment with 

        Returns:
            Dict
        """
        pass

    @abc.abstractmethod
    def verify(self, transaction: TransactionModel) -> Tuple[bool, Optional[dict]]:
        """
        Verify a payment

        Args:
            transaction: Transaction Model

        Returns:
            Tuple[bool, Optional[dict]] 
        """

        # give a sample output
        pass

    @abc.abstractmethod
    def withdraw(self, amount: int) -> bool:
        """
        Withdraw funds from the wallet
        to the user's personal account

        Args:
            amount(int): Integer amount to transfer

        Returns:
            Any
        """
        pass
