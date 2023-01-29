from rest_framework.test import APITestCase
from django.urls import reverse
from jarvis.apis.output import (
    PromptOutputListAPIView,
    PromptOutputRetrieveAPIView
)
from jarvis.models import (
    PromptOutputModel
)
from jarvis.models.abstract import AbstractPromptModel
from account.models import User, Seller
from jarvis.serializers.output import PromptOutputSerializer

from rest_framework.permissions import IsAuthenticated
from account.permissions import IsVerified


class PromptOutputTestCase(APITestCase):
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

        self.output: PromptOutputModel = PromptOutputModel.objects.create(
            uid="id1",  # type: ignore
            user=self.user,
            model_name=AbstractPromptModel.Names.GPT3,
            model_input="xxx",
            input={'prompt': 'test prompt 1'},
            output='test output 1',
            cost=0.0,
            type=AbstractPromptModel.Types.TEXT,
            model_user=self.user,
            model_snapshot={}
        )

        self.list_url = reverse("jarvis:prompt-output-list")
        self.detail_url = reverse("jarvis:prompt-output-detail", kwargs={
            "pk": self.output.pk
        })

    def test_permission_classes(self):
        self.assertEqual(
            PromptOutputListAPIView.permission_classes,
            [IsAuthenticated, IsVerified]
        )
        self.assertEqual(
            PromptOutputRetrieveAPIView.permission_classes,
            [IsAuthenticated, IsVerified]
        )

    def test_serializers(self):
        self.assertEqual(
            PromptOutputListAPIView.serializer_class,
            PromptOutputSerializer
        )

        self.assertEqual(
            PromptOutputRetrieveAPIView.serializer_class,
            PromptOutputSerializer
        )

    def test_prompt_output_list(self):
        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 1)  # type: ignore

    def test_prompt_output_list_search(self):
        self.client.force_authenticate(user=self.user)  # type: ignore
        search = "test prompt"
        response = self.client.get(self.list_url + f"?search={search}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 1)  # type: ignore

    def test_prompt_output_list_search_2(self):
        """ Ensure that the model_input is not searchable"""
        self.client.force_authenticate(user=self.user)  # type: ignore
        search = self.output.model_input
        response = self.client.get(self.list_url + f"?search={search}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.json()["results"]), 0,
            "The model_input should not be searchable"
        )

    def test_prompt_output_detail(self):
        self.client.force_authenticate(user=self.user)  # type: ignore
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"],
                         self.output.id)  # type: ignore
