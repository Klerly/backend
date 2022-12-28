
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from core.response import SuccessResponse
from account.serializers.auth.general import (
    GeneralSignUpSerializer,
    GeneralSignInSerializer,
)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from typing import List, Any
from account.modules.mail.template import AccountMailTemplate
from account.models import User
from account.models import EmailTokenVerificationModel, ResetPasswordTokenVerificationModel
import re
from django.contrib.auth import password_validation
from core.exceptions import HttpValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import HttpRequest


class GeneralSignUpAPI(generics.CreateAPIView):
    permission_classes: List[Any] = []
    serializer_class = GeneralSignUpSerializer
    queryset = get_user_model().objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return SuccessResponse(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class GeneralSignInAPI(generics.CreateAPIView):
    permission_classes: List[Any] = []
    serializer_class = GeneralSignInSerializer
    queryset = get_user_model().objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user: User = serializer.validated_data['user']
        data = user.login()
        return SuccessResponse(data)


class GeneralSignOutAPI(APIView):
    permission_classes: List[Any] = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user: User = request.user
        user.logout()
        return SuccessResponse(
            'You have been logged out successfully'
        )


class SendVerificationEmailAPI(APIView):
    permission_classes: List[Any] = []

    def get(self, request, *args, **kwargs):
        email = request.GET.get('email')
        if not email:
            return HttpValidationError({'email': ['An email is required']})
        try:
            user: User = get_user_model().objects.get(email=email)  # type: ignore
        except get_user_model().DoesNotExist:
            raise HttpValidationError('User with this email does not exist')
        if user.is_active:
            raise HttpValidationError('This email is already verified')

        AccountMailTemplate.VerifyEmail(user).send()
        return SuccessResponse('A verification email has been sent to you. If you can\'t find it, please check your spam folder.')


class CheckVerificationEmailTokenAPI(APIView):
    permission_classes: List[Any] = []

    def get(self, request, *args, **kwargs):
        token = request.GET.get('token')
        email = request.GET.get('email')
        if not token or not email:
            raise HttpValidationError('Token and email are required')
        try:
            user: User = get_user_model().objects.get(email=email)  # type: ignore
        except get_user_model().DoesNotExist:
            raise HttpValidationError('User with this email does not exist')
        if user.is_active:
            raise HttpValidationError('This email is already verified')

        try:

            token_obj: EmailTokenVerificationModel = user.email_token_verification  # type: ignore
        except EmailTokenVerificationModel.DoesNotExist:
            raise HttpValidationError(
                'The token you entered is not valid. Please enter a valid one or request a new one'
            )

        if not token_obj.is_valid(token):  # type: ignore
            raise HttpValidationError(
                'The token you entered is invalid or may have expired. Please enter a valid one or request a new one'
            )

        token_obj.delete()
        user.activate()
        return SuccessResponse(
            'Yay, your account has been verified. Sign in to continue'
        )


class SendResetPasswordEmailAPI(APIView):
    permission_classes: List[Any] = []

    def get(self, request, *args, **kwargs):
        email = request.GET.get('email')
        if not email:
            raise HttpValidationError(
                {'email': ['An valid email is required']}
            )

        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            raise HttpValidationError(
                {'email': ['An valid email is required']}
            )

        try:
            user: User = get_user_model().objects.get(email=email)  # type: ignore
        except get_user_model().DoesNotExist:
            raise HttpValidationError(
                'Unfortunately, we couldn\'t find a user with this email address'
            )

        AccountMailTemplate.ResetPassword(user).send()
        return SuccessResponse(
            'A reset password email has been sent to you. If you can\'t find it, please make sure to check your spam folder.'
        )


class CheckResetPasswordEmailTokenAPI(APIView):

    permission_classes: List[Any] = []

    def get(self, request, *args, **kwargs):
        self.__check(request)
        return SuccessResponse(
            'Yay, your reset password token is valid. Please proceed to reset your password'
        )

    def post(self, request, *args, **kwargs):
        user, token_obj = self.__check(request)
        password = request.data.get('password')
        if not password:
            raise HttpValidationError({'password': ['A password is required']})

        try:
            password_validation.validate_password(password)
        except DjangoValidationError as e:
            raise HttpValidationError({"password": e.messages})

        user.set_password(password)
        user.save()
        token_obj.delete()
        return SuccessResponse(
            'Your password has been reset successfully. Please sign in to continue'
        )

    def __check(self, request: HttpRequest):
        token = request.GET.get('token')
        email = request.GET.get('email')
        if not token or not email:
            raise HttpValidationError('A token and email are required')
        try:
            user: User = get_user_model().objects.get(email=email)  # type: ignore
        except get_user_model().DoesNotExist:
            raise HttpValidationError(
                'Unfortunately, we couldn\'t find a user with this email address'
            )
        try:
            token_obj: ResetPasswordTokenVerificationModel = user.reset_password_token_verification  # type: ignore
        except ResetPasswordTokenVerificationModel.DoesNotExist:
            raise HttpValidationError(
                'The reset password token is invalid. Please enter a valid one or request a new one'
            )
        if not token_obj.is_valid(token):  # type: ignore
            raise HttpValidationError(
                'The reset password token is invalid. Please enter a valid one or request a new one'
            )

        return user, token_obj


class TestAuthenticatedAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return SuccessResponse('Nice')
