from rest_framework.test import APITestCase
from account.models import User
from account.serializers.user import UserSerializer
from django.utils import timezone


class UserSerializerTestCase(APITestCase):
    def setUp(self):
        self.user: User = User.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            is_verified=True,
            last_login=timezone.now(),
        )

    def test_serializer_with_instance(self):
        serializer = UserSerializer(instance=self.user)
        # check that the password field is not present
        self.assertNotIn('password', serializer.data)
        # check that other fields are present
        self.assertEqual(serializer.data['email'], self.user.email)
        self.assertEqual(serializer.data['first_name'], self.user.first_name)
        self.assertEqual(serializer.data['last_name'], self.user.last_name)
        self.assertEqual(serializer.data['is_verified'], self.user.is_verified)

    def test_serializer_read_only_fields(self):
        tomorrow = timezone.now() + timezone.timedelta(days=1)
        serializer = UserSerializer(self.user, data={
            'last_login': tomorrow,
            'date_joined': tomorrow,
        }, partial=True)  # type: ignore
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertEqual(user.last_login, self.user.last_login)
        self.assertEqual(user.date_joined, self.user.date_joined)
