from rest_framework import serializers
from jarvis.models import (
    GPT3PromptModel,
    GPT3PromptOutputModel
)
from jarvis.serializers import GPT3PromptSellerSerializer
from jarvis.serializers.abstract import AbstractPromptSellerSerializer

from django.test import TestCase
from jarvis.models import GPT3PromptOutputModel
from account.models import User


class GPT3PromptSellerSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(  # type:ignore
            email='testuser@email.com',
            username='testuser',
            password='testpassword')
        self.prompt_data = {
            "icon": "https://www.google.com",
            "heading": "Sample Heading",
            "description": "Sample Description",
            "template": """
                This is a sample template
                Generate a business name acronym: {prompt}
                """,
            "template_params": [
                    {
                        "name": "prompt",
                        "description": "The name of the business"
                    }
            ],
            "user": self.user,
            "model": GPT3PromptModel.Models.DAVINCI_003
        }
        self.prompt = GPT3PromptModel.objects.create(
            **self.prompt_data
        )
        self.output1 = GPT3PromptOutputModel.objects.create(
            uid="id1",  # type: ignore
            user=self.user,
            model=self.prompt,
            model_input="xxx",
            input={'prompt': 'test prompt 1'},
            output='test output 1',
            cost=0.0,
            model_snapshot={}
        )
        self.request = type('Request', (object,), {
            'user': self.user
        })

    def test_class_inheritance(self):
        self.assertTrue(
            issubclass(GPT3PromptSellerSerializer,
                       AbstractPromptSellerSerializer)
        )

    def test_create(self):
        data = {
            "icon": "https://www.google.com",
            "heading": "Sample Heading",
            "description": "Sample Description",
            "template": """
                This is a sample template
                Generate a business name acronym: {prompt}
                """,
            "template_params": [
                    {
                        "name": "prompt",
                        "description": "The name of the business"
                    }
            ],
            "user": self.user,
            "model": GPT3PromptModel.Models.DAVINCI_003
        }
        serializer = GPT3PromptSellerSerializer(
            data=data,
            context={'request': self.request}
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(GPT3PromptModel.objects.count(), 2)

    def test_update(self):
        data = {
            "icon": "https://www.google.com",
            "heading": "Sample Heading",
            "description": "Sample Description",
            "template": """
                This is a sample template
                Generate a business name acronym: {updated_prompt_param}
                """,
            "template_params": [
                    {
                        "name": "updated_prompt_param",
                        "description": "The name of the business"
                    }
            ],
        }
        serializer = GPT3PromptSellerSerializer(
            instance=self.prompt,
            data=data,
            context={'request': self.request}
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(GPT3PromptModel.objects.count(), 1)
        self.assertEqual(
            GPT3PromptModel.objects.first(
            ).template_params[0]['name'],  # type: ignore
            'updated_prompt_param'
        )
