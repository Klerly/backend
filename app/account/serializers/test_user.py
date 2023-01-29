from rest_framework.test import APITestCase
from django.test import TestCase
from account.models import User, Seller
from account.serializers.user import (
    UserSerializer,
    SellerSerializer,
    PublicSellerSerializer,
)
from django.utils import timezone
from rest_framework.exceptions import ValidationError


class UserSerializerTestCase(APITestCase):
    def setUp(self):
        self.user: User = User.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            is_verified=True,
            last_login=timezone.now()
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
        self.assertEqual(serializer.data['seller_profile'], None)

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


class SellerSerializerTestCase(APITestCase):
    def setUp(self):
        self.user: User = User.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            is_verified=True,
            last_login=timezone.now(),
        )
        self.seller: Seller = Seller.objects.create(  # type: ignore
            user=self.user,
            handle='testhandle',
            name='Test Name',
        )
        self.user.refresh_from_db()
        self.request = self.client.get('/').wsgi_request
        self.request.user = self.user

    def test_earnings(self):
        self.assertEqual(self.seller.earnings, 0)
        # ensure that earnings is a read only field
        self.assertIn(
            'earnings',
            SellerSerializer.Meta.read_only_fields
        )

        # check that the earnings are not updated
        serializer = SellerSerializer(self.seller, data={
            'earnings': 100,
        }, partial=True)  # type: ignore
        self.assertTrue(serializer.is_valid())
        seller = serializer.save()
        self.assertEqual(seller.earnings, 0)

    def test_pending_earnings(self):
        self.assertEqual(self.seller.pending_earnings, 0)
        # ensure that pending_earnings is a read only field
        self.assertIn(
            'pending_earnings',
            SellerSerializer.Meta.read_only_fields
        )

        # check that the pending_earnings are not updated
        serializer = SellerSerializer(self.seller, data={
            'pending_earnings': 100,
        }, partial=True)   # type: ignore
        self.assertTrue(serializer.is_valid())
        seller = serializer.save()
        self.assertEqual(seller.pending_earnings, 0)

    def test_validate_handle_spaces(self):
        data = {
            'handle': 'test handle',
        }
        serializer = SellerSerializer(data=data)  # type: ignore
        self.assertFalse(serializer.is_valid())
        self.assertIn('handle', serializer.errors)
        self.assertIn(
            'cannot contain spaces',
            serializer.errors['handle'][0],
        )

    def test_validate_handle_special_characters(self):
        handles = [
            'test@handle', 'test!handle', 'test#handle', 'test$handle',
            'test^handle', 'test&handle', 'test*handle', 'test(handle',
            'test)handle', 'test+handle', 'test=handle', 'test{handle',
            'test}handle', 'test[handle', 'test]handle', 'test|handle',
            'test\\handle', 'test/handle', 'test?handle', 'test>handle',
            'test%handle', 'test~handle', 'test`handle', 'test:handle',
            'test;handle', 'test"handle', 'test\'handle', 'test,handle',
            'test.handle', 'test<handle',
        ]
        for handle in handles:
            data = {
                'handle': handle,
            }
            serializer = SellerSerializer(data=data)  # type: ignore
            self.assertFalse(serializer.is_valid())
            self.assertIn('handle', serializer.errors)
            self.assertIn(
                'cannot contain special characters',
                serializer.errors['handle'][0],
            )

    def test_create(self):

        user = User.objects.create(
            email='test2@example.com',
            username='test2@example.com',
            first_name='Test',
            last_name='User',
        )
        self.request.user = user
        data = {
            'handle': 'testhandle2',
            'name': 'Test Name',
            'about': 'Test About',
        }
        serializer = SellerSerializer(
            data=data,  # type: ignore
            context={'request': self.request},
        )
        self.assertTrue(serializer.is_valid())
        seller: Seller = serializer.save()
        self.assertEqual(seller.handle, data['handle'])
        self.assertEqual(seller.name, data['name'])
        self.assertEqual(seller.about, data['about'])
        self.assertEqual(seller.user, user)  # type: ignore

    def test_create_exisiting_user_profile(self):
        data = {
            'handle': 'testhandle3',
            'name': 'Test Name',
            'about': 'Test About',
        }
        serializer = SellerSerializer(
            data=data,  # type: ignore
            context={'request': self.request},
        )
        serializer.is_valid()
        with self.assertRaises(ValidationError) as context:
            serializer.save()
        self.assertIn(
            'already have a seller profile',
            str(context.exception),
        )

    def test_use_existing_handle(self):
        data = {
            'handle': 'testhandle',
        }
        serializer = SellerSerializer(data=data)  # type: ignore
        self.assertFalse(serializer.is_valid())
        self.assertIn('handle', serializer.errors)
        self.assertIn(
            'already exists',
            serializer.errors['handle'][0],
        )

    def test_update_handle(self):
        data = {
            'handle': 'testhandle',
        }
        serializer = SellerSerializer(
            instance=self.seller,
            data=data,  # type: ignore
            partial=True
        )

        self.assertTrue(serializer.is_valid())
        with self.assertRaises(ValidationError) as context:
            serializer.save()
        self.assertIn(
            'cannot change your handle',
            str(context.exception),
        )

    def test_update(self):
        data = {
            'name': 'Test Name2',
            'about': 'Test About2',
        }
        serializer = SellerSerializer(
            instance=self.seller,
            data=data,  # type: ignore
            context={'request': self.request},
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        seller: Seller = serializer.save()
        self.assertEqual(seller.name, data['name'])
        self.assertEqual(seller.about, data['about'])
        self.assertEqual(seller.user, self.user)  # type: ignore

    def test_deactivate(self):
        self.assertTrue(self.seller.is_active)

        serializer = SellerSerializer(
            instance=self.seller,
            data={'is_active': False},  # type: ignore
            context={'request': self.request},
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        seller: Seller = serializer.save()
        self.assertFalse(seller.is_active)


class PublicSellerSerializerTests(TestCase):

    def setUp(self):
        self.user: User = User.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            is_verified=True,
            last_login=timezone.now(),
        )
        self.seller: Seller = Seller.objects.create(  # type: ignore
            user=self.user,
            handle='testhandle',
            name='Test Name',
        )

    def test_fields(self):
        fields = [
            "name",
            "handle",
            "about",
        ]

        serializer = PublicSellerSerializer(self.seller)  # type: ignore
        self.assertEqual(set(serializer.data.keys()), set(fields))
