from rest_framework import serializers
from django.contrib.auth import get_user_model
from account.models import Seller
from django.core.exceptions import ObjectDoesNotExist
from account.models import User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        read_only_fields = (
            'date_joined',
            'last_login',
            'seller_profile',
        )
        fields = read_only_fields + (
            'email',
            'first_name',
            'last_name',
            'is_verified',
        )


class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        read_only_fields = (
            "pending_earnings",
            "earnings",
            "user",
        )
        fields = read_only_fields + (
            'is_active',
            'handle',
            'name',
            'about',
        )

    def validate_handle(self, value):
        import re
        if ' ' in value:
            raise serializers.ValidationError(
                'The handle cannot contain spaces'
            )

        if bool(re.match('^[a-zA-Z0-9_]+$', value)) is False:
            raise serializers.ValidationError(
                'The handle cannot contain special characters'
            )

        return value

    def create(self, validated_data):
        user: User = self.context['request'].user
        if user.is_seller():
            raise serializers.ValidationError(
                'You already have a seller profile'
            )
        validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'handle' in validated_data:
            raise serializers.ValidationError(
                'You cannot change your handle'
            )
        return super().update(instance, validated_data)


class PublicSellerSerializer(serializers.Serializer):
    handle = serializers.CharField()
    name = serializers.CharField()
    about = serializers.CharField()

    def to_representation(self, instance):
        return {
            'handle': instance.handle,
            'name': instance.name,
            'about': instance.about,
        }
