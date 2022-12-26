
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from account.serializers.auth.general import (
    GeneralSignUpSerializer,
    GeneralSignInSerializer,
)
from account.models import TokenProxyModel
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from typing import List, Any
from core.modules.mail.templates import MailT
from django.contrib.auth.models import User
from account.models import EmailTokenVerificationModel, ResetPasswordVerificationModel
# import django request
from django.http import HttpRequest
from django.contrib.auth import password_validation
from rest_framework.serializers import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError


class GeneralSignUpAPI(generics.CreateAPIView):
    permission_classes: List[Any] = []
    serializer_class = GeneralSignUpSerializer
    queryset = get_user_model().objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class GeneralSignInAPI(generics.CreateAPIView):
    permission_classes: List[Any] = []
    serializer_class = GeneralSignInSerializer
    queryset = get_user_model().objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        try:
            token = TokenProxyModel.objects.get(user=user)
            if token.has_almost_expired() or token.has_expired():
                token.delete()
                token = TokenProxyModel.objects.create(user=user)
        except TokenProxyModel.DoesNotExist:
            token = TokenProxyModel.objects.create(user=user)

        token, _ = TokenProxyModel.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'is_active': user.is_active
        }, status=status.HTTP_200_OK)


class SendVerificationEmailAPI(APIView):
    permission_classes: List[Any] = []

    def get(self, request, *args, **kwargs):
        email = request.GET.get('email')
        if not email:
            return Response({'message': 'An email is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user: User = get_user_model().objects.get(email=email)  # type: ignore
        except get_user_model().DoesNotExist:
            raise ValidationError(
                {'non_field_errors': ['User with this email does not exist']})
        if user.is_active:
            raise ValidationError(
                {'non_field_errors': ['This email is already verified']})

        MailT.VerifyEmail(user).send()
        return Response({
            'message': 'A verification email has been sent to you. If you can\'t find it, please check your spam folder.'},
            status=status.HTTP_200_OK
        )


class CheckVerificationEmailTokenAPI(APIView):
    permission_classes: List[Any] = []

    def get(self, request, *args, **kwargs):
        token = request.GET.get('token')
        email = request.GET.get('email')
        if not token or not email:
            raise ValidationError(
                {'non_field_errors': ['Token and email are required']})
        try:
            user: User = get_user_model().objects.get(email=email)  # type: ignore
        except get_user_model().DoesNotExist:
            raise ValidationError(
                {'non_field_errors': ['User with this email does not exist']})
        if user.is_active:
            raise ValidationError(
                {'non_field_errors': ['This email is already verified']})

        try:

            token_obj: EmailTokenVerificationModel = user.email_token_verification  # type: ignore
        except EmailTokenVerificationModel.DoesNotExist:
            raise ValidationError({'non_field_errors': [
                                  'The verification token is invalid. Please enter a valid one or request a new one']}
                                  )

        if not token_obj.is_valid(token):  # type: ignore
            raise ValidationError({'non_field_errors': [
                                  'The verification token is invalid. Please enter a valid one or request a new one']}
                                  )

        token_obj.delete()
        user.is_active = True
        user.save()
        return Response({
            'message': 'Yay, your account has been verified. Sign in to continue'},
            status=status.HTTP_200_OK
        )


class SendResetPasswordEmailAPI(APIView):
    permission_classes: List[Any] = []

    def get(self, request, *args, **kwargs):
        email = request.GET.get('email')
        if not email:
            raise ValidationError(
                {'non_field_errors': ['An email is required']}
            )

        try:
            user: User = get_user_model().objects.get(email=email)  # type: ignore
        except get_user_model().DoesNotExist:
            raise ValidationError(
                {'non_field_errors': ['Unfortunately, we couldn\'t find a user with this email address']})

        MailT.ResetPassword(user).send()
        return Response({
            'message': 'A reset password email has been sent to you. If you can\'t find it, please make sure to check your spam folder.'},
            status=status.HTTP_200_OK
        )


class CheckResetPasswordEmailTokenAPI(APIView):

    permission_classes: List[Any] = []

    def get(self, request, *args, **kwargs):
        self.__check(request)
        return Response({
            'message': 'Yay, your reset password token is valid. Please proceed to reset your password'},
            status=status.HTTP_200_OK
        )

    def post(self, request, *args, **kwargs):
        user, token_obj = self.__check(request)
        password = request.data.get('password')
        if not password:
            raise ValidationError(
                {'non_field_errors', 'A password is required'})

        try:
            password_validation.validate_password(password)
        except DjangoValidationError as e:
            raise ValidationError({"password": e.messages})

        user.set_password(password)
        user.save()
        token_obj.delete()
        return Response({
            'message': 'Your password has been reset successfully. Please sign in to continue'},
            status=status.HTTP_200_OK
        )

    def __check(self, request: HttpRequest):
        token = request.GET.get('token')
        email = request.GET.get('email')
        if not token or not email:
            raise ValidationError('A token and email are required')
        try:
            user: User = get_user_model().objects.get(email=email)  # type: ignore
        except get_user_model().DoesNotExist:
            raise ValidationError({
                'non_field_errors': ['Unfortunately, we couldn\'t find a user with this email address']
            })
        try:
            token_obj: ResetPasswordVerificationModel = user.reset_password_token_verification  # type: ignore
        except ResetPasswordVerificationModel.DoesNotExist:
            raise ValidationError(
                {'non_field_errors': [
                    'The reset password token is invalid. Please enter a valid one or request a new one'
                ]}
            )
        if not token_obj.is_valid(token):  # type: ignore
            raise ValidationError(
                {'non_field_errors': [
                    'The reset password token is invalid. Please enter a valid one or request a new one'
                ]}
            )

        return user, token_obj


class TestAuthenticatedAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        return Response({'message': 'Nice'}, status=status.HTTP_200_OK)
        # return Response({'message': 'You are authenticated'}, status=status.HTTP_200_OK)
