from django.contrib import admin
from wallet.models import WalletModel, TransactionModel, CardModel

admin.site.register(WalletModel)
admin.site.register(TransactionModel)
admin.site.register(CardModel)
