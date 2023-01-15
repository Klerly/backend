from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation


class GeneralSignUpSerializer(serializers.Serializer):
    """ Create a new user using email,
        password, first_name, last_name.
    """
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=300)
    last_name = serializers.CharField(max_length=300)
    password = serializers.CharField(write_only=True, max_length=300)

    def validate_email(self, value):
        if get_user_model().objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'A user with this email already exists'
            )
        return value

    def validate_password(self, value):
        password_validation.validate_password(value, self.instance)
        return value

    def create(self, validated_data):
        user = get_user_model().objects.create_user(  # type: ignore
            email=validated_data['email'],
            username=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            is_active=True
        )
        return user


class GeneralSignInSerializer(serializers.Serializer):
    """ Sign in a user using email and password.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, max_length=300)

    class Exception:
        class Messages:
            INVALID_CREDENTIALS = 'Invalid username or password'

    def validate_email(self, value):
        if not get_user_model().objects.filter(email=value).exists():
            raise serializers.ValidationError(
                self.Exception.Messages.INVALID_CREDENTIALS
            )
        return value

    def validate(self, data):
        user = get_user_model().objects.get(email=data['email'])
        if not user.check_password(data['password']):
            raise serializers.ValidationError(
                self.Exception.Messages.INVALID_CREDENTIALS
            )
        data['user'] = user
        return data
