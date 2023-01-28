# from jarvis.models import AbstractPromptModel, CompletionModel
from django.test import TestCase
from jarvis.models import (
    AbstractPromptModel,
    GPT3PromptModel,
    GPT3PromptOutputModel
)
from account.models import User, Seller
from unittest.mock import patch
from typing import Union


class GPT3PromptModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(  # type: ignore
            username="testuser",
            email="testuser@email.co",
            password="testpassword"
        )
        self.seller: Seller = Seller.objects.create(  # type: ignore
            user=self.user,
            handle='testhandle',
            name='Test Name',
        )
        self.concrete_model = GPT3PromptModel
        self.prompt: Union[AbstractPromptModel, GPT3PromptModel] = self.concrete_model.objects.create(
            icon="https://www.google.com",
            heading="Sample Heading",
            description="Sample Description",
            template="""
            Generate a business name acronym: {business_name}
            I am into {business_type} and I need a name and slogan and catchy slogan for my business.
            Make it catchy and memorable.
            E.g 1. "Orange Group" is a business that does everything.

            """,
            template_params=[
                {
                    "name": "business_name",
                    "description": "The name of the business"
                },
                {
                    "name": "business_type",
                    "description": "The type of business"
                }
            ],
            user=self.user
        )

    def test_create(self):
        self.assertEqual(self.concrete_model.objects.count(), 1)

    def test_validate_model(self):
        with self.assertRaises(ValueError) as context:
            self.prompt.model = "non-existent-model"  # type: ignore
            self.prompt._validate_model()  # type: ignore

    def test_generate(self):
        with patch(
            "openai.Completion.create",
            return_value={
                "choices": [{
                    "finish_reason": "stop",
                    "index": 0,
                    "logprobs": None,
                    "text": "\nVIT GROUP - \"Vitaminize Your Life!\""
                }],
                "created": 1674607188,
                "id": "cmpl-6cO7IgHw7Es0IMB2aO7XMOCxWKvTU",
                "model": "text-davinci-003",
                "object": "text_completion",
                "usage": {
                "completion_tokens": 12,
                "prompt_tokens": 62,
                "total_tokens": 74
                }
            }

        ) as mock:
            self.prompt.generate(
                business_name="Vitamin Group",
                business_type="We provide vitamin supplements"
            )
            mock.assert_called_once_with(
                model=self.prompt.model,  # type: ignore
                temperature=self.prompt.temparature,  # type: ignore
                max_tokens=self.prompt.max_tokens,  # type: ignore
                top_p=self.prompt.top_p,  # type: ignore
                frequency_penalty=self.prompt.frequency_penalty,  # type: ignore
                presence_penalty=self.prompt.presence_penalty,  # type: ignore
                user=str(self.user.id),
                prompt=self.prompt.get_prompt(
                    business_name="Vitamin Group",
                    business_type="We provide vitamin supplements"
                ),
                echo=False,
                stream=False,
            )

            self.assertEqual(GPT3PromptOutputModel.objects.count(), 1)

    def test_delete(self):
        self.assertEqual(
            self.concrete_model.objects.first().is_active,  # type: ignore
            1
        )
        self.prompt.delete()
        self.assertEqual(
            self.concrete_model.objects.first().is_active,  # type: ignore
            0
        )
