from django.urls import reverse
from rest_framework.test import APIClient, APIRequestFactory
from wallet.models import CardModel, WalletModel
from account.models import User
from wallet.apis.card import CardRetrieveUpdateDestroyAPI, CardListAPI
from django.test import TestCase


class CardListAPITestCase(TestCase):
    card_data = {
        "keep": False,
        "type": 'Visa',
        "last_four": '1234',
        "exp_month": '01',
        "exp_year": '2022',
        "authorization_code": 'authcode',
        "data": {'last4': '1234', 'exp_month': '01', 'exp_year': '2022',
                     'authorization_code': 'authcode', 'signature': 'signature'}
    }

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(  # type: ignore
            username='testuser',
            password='password',
            is_verified=True
        )  # type: ignore
        self.client = APIClient()
        self.wallet = WalletModel.objects.create(user=self.user)
        self.card1 = CardModel.objects.create(
            user=self.user,
            signature='signature1',
            **self.card_data
        )
        self.card2 = CardModel.objects.create(
            user=self.user,
            signature='signature2',
            **self.card_data
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('wallet:card-list')

    def test_get_queryset(self):
        view = CardListAPI()
        view.request = self.factory.get(self.url)
        view.request.user = self.user

        queryset = view.get_queryset()

        self.assertEqual(list(queryset), [self.card1, self.card2])

    def test_get_queryset_different_user(self):
        user2 = User.objects.create_user(  # type: ignore
            username='testuser2',
            email='testuser2@mail.com',
            password='password'
        )
        view = CardListAPI()
        view.request = self.factory.get(self.url)
        view.request.user = user2
        queryset = view.get_queryset()
        self.assertEqual(list(queryset), [])

    def test_list_cards(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)  # type: ignore


class CardRetrieveUpdateDestroyAPITestCase(TestCase):
    card_data = {
        "keep": False,
        "type": 'Visa',
        "last_four": '1234',
        "exp_month": '01',
        "exp_year": '2022',
        "authorization_code": 'authcode',
        "data": {'last4': '1234', 'exp_month': '01', 'exp_year': '2022',
                     'authorization_code': 'authcode', 'signature': 'signature'}
    }

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(  # type: ignore
            username='testuser',
            password='password',
            is_verified=True
        )  # type: ignore
        self.client = APIClient()
        self.wallet = WalletModel.objects.create(user=self.user)
        self.card1 = CardModel.objects.create(
            user=self.user,
            signature='signature1',
            **self.card_data
        )
        self.card2 = CardModel.objects.create(
            user=self.user,
            signature='signature2',
            **self.card_data
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('wallet:card-detail', args=[self.card1.pk])

    def test_get_queryset(self):
        view = CardRetrieveUpdateDestroyAPI()
        view.request = self.factory.get('/')
        view.request.user = self.user

        queryset = view.get_queryset()

        self.assertEqual(list(queryset), [self.card1, self.card2])

    def test_get_queryset_different_user(self):
        user2 = User.objects.create_user(  # type: ignore
            username='testuser2',
            email='testuser2@mail.com',
            password='password'
        )
        view = CardRetrieveUpdateDestroyAPI()
        view.request = self.factory.get(self.url)
        view.request.user = user2
        queryset = view.get_queryset()
        self.assertEqual(list(queryset), [])

    def test_retrieve_card(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_update_card(self):
        data = {'keep': True}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['keep'], True)  # type: ignore

    def test_delete_card(self):
        self.assertEqual(CardModel.objects.count(), 2)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(CardModel.objects.count(), 1)
