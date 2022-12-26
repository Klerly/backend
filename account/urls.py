from django.urls import path
from account import apis

app_name = 'account'
urlpatterns = [
    path('auth/general/sign-up', apis.GeneralSignUpAPI.as_view(),
         name='account-general-signup'),
    path('auth/general/sign-in', apis.GeneralSignInAPI.as_view(),
         name='account-general-signin'),
    path('auth/general/verification/mail/email-verification', apis.SendVerificationEmailAPI.as_view(),
         name='account-general-send-verification-email'),
    path('auth/general/verification/mail/reset-password', apis.SendResetPasswordEmailAPI.as_view(),
         name='account-general-send-reset-password-email'),

    path('auth/general/verification/check/email-verification-token', apis.CheckVerificationEmailTokenAPI.as_view(),
         name='account-general-check-verification-email-token'),
    path('auth/general/verification/check/reset-password-token', apis.CheckResetPasswordEmailTokenAPI.as_view(),
         name='account-general-check-reset-password-email-token'),

    path('auth/general/test-authenticated', apis.TestAuthenticatedAPI.as_view(),
         name='account-general-test-authenticated'),
]
