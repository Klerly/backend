from account.models import User
from wallet.serializers.card import CardSerializer
from django.contrib.auth import get_user_model
from wallet.models import CardModel
from django.test import TestCase


class CardSerializerTest(TestCase):
    def setUp(self):
        self.user: User = get_user_model().objects.create_user(  # type: ignore
            username='testuser@user.com',
            email='testuser@user.com',
            password='testpassword'
        )
        self.card = CardModel.objects.create(
            user=self.user,
            keep=True,
            type='Visa',
            last_four='1234',
            exp_month='01',
            exp_year='2022',
            authorization_code='authcode',
            signature='signature',
            data={'last4': '1234', 'exp_month': '01', 'exp_year': '2022',
                  'authorization_code': 'authcode', 'signature': 'signature'}
        )
        self.serializer = CardSerializer(instance=self.card)
        self.data = self.serializer.data

    def test_contains_expected_fields(self):
        # Ensure the serializer contains the correct fields
        fields = set(['keep', 'type', 'last_four', 'created_at',
                     'signature'])
        self.assertEqual(set(self.data.keys()), fields)

        # Ensure that incorrect fields are not present
        invalid_fields = set(['user', 'exp_month', 'exp_year',
                              'authorization_code', 'data'])
        self.assertFalse(invalid_fields.intersection(self.data.keys()))

    def test_update_fields(self):
        data = {'last_four': '4321', 'exp_month': '02',
                'exp_year': '2023', 'keep': False,
                'authorization_code': 'newcode', 'signature': 'newsignature'}
        serializer = CardSerializer(
            instance=self.card, data=data, partial=True)  # type: ignore
        serializer.is_valid()
        serializer.save()

        # Ensure that the read-only fields are not updated
        self.assertEqual(self.card.last_four, '1234')
        self.assertEqual(self.card.exp_month, '01')
        self.assertEqual(self.card.exp_year, '2022')
        self.assertEqual(self.card.authorization_code, 'authcode')
        self.assertEqual(self.card.signature, 'signature')

        # Ensure that the updated fields are updated
        self.assertEqual(self.card.keep, False)
