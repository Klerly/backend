from rest_framework import serializers
from jarvis.models import (
    Dalle2PromptModel,
    Dalle2PromptOutputModel,
)
from jarvis.serializers import (
    Dalle2PromptSellerSerializer,
    Dalle2PromptBuyerSerializer,
)
from jarvis.serializers.abstract import (
    AbstractPromptSellerSerializer,
    AbstractPromptBuyerSerializer
)

from django.test import TestCase
from jarvis.models import Dalle2PromptOutputModel
from account.models import User
from unittest import mock


class Dalle2PromptSellerSerializerTest(TestCase):
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
        }
        self.prompt = Dalle2PromptModel.objects.create(
            **self.prompt_data
        )
        self.output1 = Dalle2PromptOutputModel.objects.create(
            uid="id1",  # type: ignore
            user=self.user,
            model=self.prompt,
            model_input="xxx",
            input={'prompt': 'test prompt 1'},
            output='https://out.put/1/',
            cost=0.0,
            model_snapshot={}
        )
        self.request = type('Request', (object,), {
            'user': self.user
        })

    def test_class_inheritance(self):
        self.assertTrue(
            issubclass(Dalle2PromptSellerSerializer,
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
            "user": self.user
        }
        serializer = Dalle2PromptSellerSerializer(
            data=data,
            context={'request': self.request}
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(Dalle2PromptModel.objects.count(), 2)

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
        serializer = Dalle2PromptSellerSerializer(
            instance=self.prompt,
            data=data,
            context={'request': self.request}
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(Dalle2PromptModel.objects.count(), 1)
        self.assertEqual(
            Dalle2PromptModel.objects.first(
            ).template_params[0]['name'],  # type: ignore
            'updated_prompt_param'
        )


# class Dalle2PromptBuyerSerializer(AbstractPromptBuyerSerializer):
#     size = serializers.ChoiceField(
#         choices=Dalle2PromptModel.ImageSizes.values,
#         default=Dalle2PromptModel.ImageSizes.MEDIUM
#     )

#     class Meta(AbstractPromptBuyerSerializer.Meta):
#         model = Dalle2PromptModel
#         fields = AbstractPromptBuyerSerializer.Meta.fields + (
#             'size',
#         )

#     def generate(self) -> str:
#         instance: Union[Dalle2PromptModel,
#                         AbstractPromptModel] = self.instance  # type: ignore
#         return instance.generate(**self.validated_data)  # type: ignore


class Dalle2PromptBuyerSerializerTest(TestCase):
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
            "user": self.user
        }
        self.prompt_params = {
            "prompt": "i am a prompt parameter"
        }
        self.prompt = Dalle2PromptModel.objects.create(
            **self.prompt_data
        )

    def test_generate(self):
        data = {
            "prompt_params": self.prompt_params
        }
        serializer = Dalle2PromptBuyerSerializer(
            instance=self.prompt,
            data=data
        )
        self.assertTrue(serializer.is_valid())
        with mock.patch.object(Dalle2PromptModel, 'generate') as mock_generate:
            mock_generate.return_value = 'test output 1'
            self.assertEqual(serializer.generate(), 'test output 1')
            mock_generate.assert_called_once_with(
                **data,
                size=Dalle2PromptModel.ImageSizes.MEDIUM
            )

    def test_generate_with_size(self):
        data = {
            "prompt_params": self.prompt_params,
            "size": Dalle2PromptModel.ImageSizes.SMALL
        }
        serializer = Dalle2PromptBuyerSerializer(
            instance=self.prompt,
            data=data
        )
        self.assertTrue(serializer.is_valid())
        with mock.patch.object(Dalle2PromptModel, 'generate') as mock_generate:
            mock_generate.return_value = 'test output 1'
            self.assertEqual(serializer.generate(), 'test output 1')
            mock_generate.assert_called_once_with(
                **data,
            )
