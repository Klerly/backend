from django.urls import path
from .apis.balance import WalletBalanceAPI
from .apis.payment.crypto import (
    CryptoPaymentInitializeAPI,
    CryptoPaymentVerifyAPI,
    CryptoPaymentWebhookAPI
)
from .apis.transaction import TransactionListAPI, TransactionRetrieveAPI


app_name = 'wallet'
urlpatterns = [
    path('balance', WalletBalanceAPI.as_view(), name='balance'),

    path('payment/crypto/initialize', CryptoPaymentInitializeAPI.as_view(),
         name='payment-crypto-initialize'),
    path('payment/crypto/verify/<str:reference>',
         CryptoPaymentVerifyAPI.as_view(), name='payment-crypto-verify'),
    path('payment/crypto/webhook/kmt/', CryptoPaymentWebhookAPI.as_view(),
         name='payment-crypto-webhook'),

    path('transaction/<str:pk>', TransactionRetrieveAPI.as_view(),
         name='transaction-detail'),
    path('transaction', TransactionListAPI.as_view(), name='transaction-list'),


]
