from django.urls import path
from account import apis
from account.apis.user import (
    UserAPI,
    SellerCreateAPI,
    SellerRetrieveUpdateAPI,
    PublicSellerListAPI,
    PublicSellerRetrieveAPI
)

app_name = 'account'
urlpatterns = [
    path('auth/social/sign-in', apis.SocialSignInAPI.as_view(),
         name='account-social-signin'),
    path('auth/general/sign-up', apis.GeneralSignUpAPI.as_view(),
         name='account-general-signup'),
    path('auth/general/sign-in', apis.GeneralSignInAPI.as_view(),
         name='account-general-signin'),
    path('auth/general/sign-out', apis.GeneralSignOutAPI.as_view(),
         name='account-general-signout'),


    path('auth/general/verification/mail/email-verification', apis.SendVerificationEmailAPI.as_view(),
         name='account-general-send-verification-email'),
    path('auth/general/verification/mail/reset-password', apis.SendResetPasswordEmailAPI.as_view(),
         name='account-general-send-reset-password-email'),


    path('auth/general/verification/check/email-verification-token', apis.CheckVerificationEmailTokenAPI.as_view(),
         name='account-general-check-verification-email-token'),
    path('auth/general/verification/check/reset-password-token', apis.CheckResetPasswordEmailTokenAPI.as_view(),
         name='account-general-check-reset-password-email-token'),

    path('user', UserAPI.as_view(), name='account-user'),

    path('user/seller', SellerCreateAPI.as_view(),
         name='account-seller-create'),
    path('user/seller/me', SellerRetrieveUpdateAPI.as_view(),
         name='account-seller-detail'),

    path('seller', PublicSellerListAPI.as_view(),
         name='account-public-seller-list'),
    path('seller/<str:handle>', PublicSellerRetrieveAPI.as_view(),
         name='account-public-seller-detail'),

]
