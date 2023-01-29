from rest_framework.test import APITestCase
from django.urls import reverse
from jarvis.apis.language.gpt3 import (
    GPT3PromptSellerListCreateAPIView,
    GPT3PromptSellerRetrieveUpdateDestroyAPIView,
    GPT3PromptBuyerListAPIView,
    GPT3PromptBuyerRetrieveAPIView
)
from jarvis.models import (
    GPT3PromptModel,
)
from account.models import User, Seller
from jarvis.serializers.language.gpt3 import (
    GPT3PromptSellerSerializer,
    GPT3PromptBuyerSerializer
)
from rest_framework.permissions import IsAuthenticated
from account.permissions import IsVerified
import json


class GPT3PromptSellerTestCase(APITestCase):
    def setUp(self) -> None:
        self.user: User = User.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            is_verified=True,
        )
        self.seller: Seller = Seller.objects.create(  # type: ignore
            user=self.user,
            handle='testhandle',
            name='Test Name',
        )
        self.prompt_data = {
            "icon": "https://www.google.com",
            "heading": "Sample Heading",
            "description": "Sample Description",
            "template": """
                This is a sample template
                Generate a business name acronym: {business_name}
                """,
            "template_params": [
                    {
                        "name": "business_name",
                        "description": "The name of the business"
                    }
            ],
            "user": self.user,
        }
        self.prompt1 = GPT3PromptModel.objects.create(
            **self.prompt_data
        )
        self.prompt2 = GPT3PromptModel.objects.create(
            **self.prompt_data
        )
        self.prompt3 = GPT3PromptModel.objects.create(
            **self.prompt_data
        )
        self.list_url = reverse("jarvis:gpt3-prompt-seller-create")
        self.detail_url = reverse("jarvis:gpt3-prompt-seller-detail", kwargs={
            "pk": self.prompt1.id
        })

    def test_permission_classes(self):
        self.assertEqual(
            GPT3PromptSellerListCreateAPIView.permission_classes,
            [IsAuthenticated, IsVerified]
        )
        self.assertEqual(
            GPT3PromptSellerRetrieveUpdateDestroyAPIView.permission_classes,
            [IsAuthenticated, IsVerified]
        )

    def test_serializers(self):
        self.assertEqual(
            GPT3PromptSellerListCreateAPIView.serializer_class,
            GPT3PromptSellerSerializer
        )

        self.assertEqual(
            GPT3PromptSellerRetrieveUpdateDestroyAPIView.serializer_class,
            GPT3PromptSellerSerializer
        )

    def test_get_queryset(self):
        # -- create a new user and prompt
        user2: User = User.objects.create(
            email='test2@example.com',
            username='test2@example.com',
            first_name='Test',
            last_name='User',
            is_verified=True,
        )

        Seller.objects.create(  # type: ignore
            user=user2,
            handle='testhandle2',
            name='Test Name',
        )
        prompt_data = self.prompt_data.copy()
        prompt_data["user"] = user2

        GPT3PromptModel.objects.create(
            **prompt_data
        )

        # -- test queryset
        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 3)  # type: ignore

        self.client.force_authenticate(user=user2)  # type: ignore
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 1)  # type: ignore

    def test_seller_prompt_list(self):
        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 3)  # type: ignore

    def test_seller_prompt_create(self):
        self.client.force_authenticate(user=self.user)  # type: ignore
        prompt_data = {
            "icon": "https://www.google.com",
            "heading": "Sample Heading",
            "description": "Sample Description",
            "template": """
                This is a sample template
                Generate a business name acronym: {business_name}
                """,
            "template_params": json.dumps([
                    {
                        "name": "business_name",
                        "description": "The name of the business"
                    }
            ]),
        }
        response = self.client.post(
            self.list_url, prompt_data)
        self.assertEqual(response.status_code, 201)

    def test_seller_prompt_detail(self):
        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"],
                         self.prompt1.id)

    def test_seller_prompt_update(self):
        self.client.force_authenticate(user=self.user)  # type: ignore
        prompt_data = {
            "icon": "https://www.icon.com"
        }
        response = self.client.patch(
            self.detail_url, prompt_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["icon"],
                         prompt_data["icon"])

    def test_seller_prompt_delete(self):
        self.client.force_authenticate(user=self.user)  # type: ignore
        self.assertTrue(self.prompt1.is_active)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 204)

        self.prompt1.refresh_from_db()
        self.assertFalse(self.prompt1.is_active)


class GPT3PromptBuyerTestCase(APITestCase):
    def setUp(self) -> None:
        self.user: User = User.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            is_verified=True,
        )
        self.seller: Seller = Seller.objects.create(  # type: ignore
            user=self.user,
            handle='testhandle',
            name='Test Name',
        )
        self.prompt_data = {
            "icon": "https://www.google.com",
            "heading": "Sample Heading",
            "description": "Sample Description",
            "template": """
                This is a sample template
                Generate a business name acronym: {business_name}
                """,
            "template_params": [
                    {
                        "name": "business_name",
                        "description": "The name of the business"
                    }
            ],
            "user": self.user,
        }
        self.prompt1 = GPT3PromptModel.objects.create(
            **self.prompt_data
        )
        self.prompt2 = GPT3PromptModel.objects.create(
            **self.prompt_data
        )
        prompt3_data = self.prompt_data.copy()
        prompt3_data["description"] = "Injurious viju milk"
        self.prompt3 = GPT3PromptModel.objects.create(
            **prompt3_data
        )

        self.list_url = reverse("jarvis:gpt3-prompt-buyer-list")
        self.detail_url = reverse("jarvis:gpt3-prompt-buyer-detail", kwargs={
            "pk": self.prompt1.id
        })

    def test_permission_classes(self):
        self.assertEqual(
            GPT3PromptBuyerListAPIView.permission_classes,
            [IsAuthenticated, IsVerified]
        )
        self.assertEqual(
            GPT3PromptBuyerRetrieveAPIView.permission_classes,
            [IsAuthenticated, IsVerified]
        )

    def test_serializers(self):
        self.assertEqual(
            GPT3PromptBuyerListAPIView.serializer_class,
            GPT3PromptBuyerSerializer
        )

        self.assertEqual(
            GPT3PromptBuyerRetrieveAPIView.serializer_class,
            GPT3PromptBuyerSerializer
        )

    def test_buyer_prompt_list(self):
        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 3)  # type: ignore

    def test_buyer_prompt_list_search(self):
        self.client.force_authenticate(user=self.user)  # type: ignore

        search = "Injurious viju milk"
        response = self.client.get(self.list_url + f"?search={search}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 1)  # type: ignore

    def test_buyer_prompt_detail(self):
        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"],
                         self.prompt1.id)
