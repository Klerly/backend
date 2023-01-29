from jarvis.models import (
    PromptOutputModel
)
from rest_framework import serializers
from account.models import Seller
from account.serializers.user import PublicSellerSerializer


class PromptOutputSerializer(serializers.ModelSerializer):
    seller = serializers.SerializerMethodField()

    class Meta:
        model = PromptOutputModel
        read_only_fields = (
            "id",
            "input",
            "output",
            "cost",
            "model_name",
            "type",
            "seller",
        )
        fields = read_only_fields
        restricted_fields = (
            "uid",
            "model_input",
            "model_snapshot",
        )

    def __init__(self, *args, **kwargs):
        if set(self.Meta.restricted_fields).intersection(set(self.Meta.fields)):
            invalid_fields = set(self.Meta.restricted_fields).intersection(
                set(self.Meta.fields)
            )
            raise AssertionError(
                """
                restricted_fields must not appear in the fields list

                To solve this issue, remove the following from the {} Meta class:

                "{}"
                """.format(
                    self.__class__.__name__,
                    ", ".join(invalid_fields)
                )
            )

        if set(self.Meta.fields).difference(set(self.Meta.read_only_fields)):
            raise AssertionError(
                """
                All fields must be read only

                To solve this issue, add the following to the {} Meta class:

                read_only_fields = AbstractPromptBuyerSerializer.Meta.read_only_fields + (
                    "your_read_only_field",
                )
                """.format(
                    self.__class__.__name__,
                    ", ".join(self.Meta.restricted_fields)
                )
            )
        super().__init__(*args, **kwargs)

    def get_seller(self, obj: PromptOutputModel):
        seller: Seller = obj.model_user.seller_profile
        return PublicSellerSerializer(seller).data
