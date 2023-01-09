from django.urls import path
from .apis.balance import WalletBalanceAPI
from .apis.payment import PaymentInitializeAPI, PaymentVerifyAPI, PaymentChargeAPI
from .apis.card import CardListAPI, CardRetrieveUpdateDestroyAPI


app_name = 'wallet'
urlpatterns = [
    path('balance', WalletBalanceAPI.as_view(), name='balance'),
    path('payment/initialize', PaymentInitializeAPI.as_view(),
         name='payment-initialize'),
    path('payment/verify/<str:reference>',
         PaymentVerifyAPI.as_view(), name='payment-verify'),
    path('payment/charge', PaymentChargeAPI.as_view(), name='payment-charge'),
    path('card/<int:pk>', CardRetrieveUpdateDestroyAPI.as_view(),
         name='card-retrieve'),
    path('card', CardListAPI.as_view(), name='card-list'),
]
