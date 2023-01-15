from rest_framework import serializers
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        read_only_fields = ('date_joined', 'last_login')
        fields = read_only_fields + (
            'email',
            'first_name',
            'last_name',
            'is_verified',
        )
