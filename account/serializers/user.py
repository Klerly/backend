from rest_framework import serializers
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'first_name', 'last_name',
                  'is_active', 'date_joined', 'last_login', 'id')
