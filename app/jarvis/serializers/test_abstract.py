from rest_framework import serializers
from jarvis.models import (
    PromptOutputModel,
    GPT3PromptModel,
)
from typing import List
from unittest import mock


from django.test import TestCase
from jarvis.models import PromptOutputModel
from jarvis.serializers.abstract import (
    AbstractPromptSellerSerializer,
    AbstractPromptBuyerSerializer
)
from account.models import User, Seller


class DummyPromptSellerSerializer(AbstractPromptSellerSerializer):
    class Meta(AbstractPromptSellerSerializer.Meta):
        model = GPT3PromptModel




class AbstractPromptSellerSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(  # type:ignore
            email='testuser@email.com',
            username='testuser',
            password='testpassword')
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
        self.prompt: GPT3PromptModel = GPT3PromptModel.objects.create(
            **self.prompt_data
        )
        self.output1 = PromptOutputModel.objects.create(
            uid="id1",  # type: ignore
            user=self.user,
            type=self.prompt.type,
            model_name=self.prompt.name,
            model_input="xxx",
            model_user=self.user,
            input={'prompt': 'test prompt 1'},
            output='test output 1',
            cost=0.0,
            model_snapshot={}
        )
        self.output2 = PromptOutputModel.objects.create(
            uid="id2",  # type: ignore
            user=self.user,
            type=self.prompt.type,
            model_name=self.prompt.name,
            model_input="xxx",
            model_user=self.user,
            input={'prompt': 'test prompt 2'},
            output='test output 2',
            cost=0.0,
            model_snapshot={}
        )
        self.output3 = PromptOutputModel.objects.create(
            uid="id3",  # type: ignore
            user=self.user,
            type=self.prompt.type,
            model_name=self.prompt.name,
            model_input="xxx",
            model_user=self.user,
            input={'prompt': 'test prompt 3'},
            output='test output 3',
            cost=0.0,
            model_snapshot={}
        )

        request = type('Request', (object,), {
            'user': self.user
        })
        self.serializer = DummyPromptSellerSerializer(
            context={'request': request},
            instance=self.prompt
        )

    def test_init(self):
        pass

    def test_validate_examples_valid(self):
        examples = [self.output2.id, self.output1.id,]
        response = self.serializer.validate_examples(examples)
        self.assertEqual(len(response), 2)
        self.assertEqual(response[0]['params'], {
            'prompt': 'test prompt 2'})
        self.assertEqual(response[0]['output'], 'test output 2')
        self.assertEqual(response[0]['type'], 'text')
        self.assertEqual(response[1]['params'], {
            'prompt': 'test prompt 1'})
        self.assertEqual(response[1]['output'], 'test output 1')
        self.assertEqual(response[1]['type'], 'text')

    def test_validate_examples_not_list(self):
        examples = "not a list"
        with self.assertRaises(serializers.ValidationError) as cm:
            self.serializer.validate_examples(examples)
        self.assertIn(cm.exception.detail[0],
                      "Examples must be a list of integers.")

    def test_validate_examples_not_int(self):
        examples = [1, 2, "3"]
        with self.assertRaises(serializers.ValidationError) as cm:
            self.serializer.validate_examples(examples)
        self.assertIn(cm.exception.detail[0],
                      "Examples must be a list of integers")

    def test_validate_examples_not_found(self):
        examples = [self.output1.id, 900039]
        with self.assertRaises(serializers.ValidationError) as cm:
            self.serializer.validate_examples(examples)
        self.assertIn(cm.exception.detail[0],
                      "One or more examples were not found")

    def test_create(self):
        # ensure that the user is set
        # when creating a new prompt

        prompt_data = self.prompt_data.copy()
        prompt_data.pop('user')
        serializer = DummyPromptSellerSerializer(
            data=prompt_data,  # type: ignore
            context={'request': self.serializer.context['request']}
        )
        self.assertTrue(serializer.is_valid())
        prompt = serializer.save()
        self.assertEqual(prompt.user, self.user)

    def test_update(self):
        # ensure that examples can be updated
        prompt_data = self.prompt_data.copy()
        prompt_data['examples'] = [self.output1.id, self.output2.id]
        # ensure that validate_examples is called

        with mock.patch.object(
            DummyPromptSellerSerializer,
            'validate_examples',
            side_effect=self.serializer.validate_examples
        ) as mock_validate_examples:

            serializer = DummyPromptSellerSerializer(
                instance=self.prompt,
                data=prompt_data,  # type: ignore
                context={'request': self.serializer.context['request']}
            )
            self.assertTrue(serializer.is_valid())
            prompt = serializer.save()
            self.assertEqual(len(prompt.examples), 2)
            self.assertEqual(prompt.examples[1]['params'], {
                'prompt': 'test prompt 1'})
            self.assertEqual(prompt.examples[1]['output'], 'test output 1')
            self.assertEqual(prompt.examples[1]['type'], 'text')
            self.assertEqual(prompt.examples[0]['params'], {
                'prompt': 'test prompt 2'})
            self.assertEqual(prompt.examples[0]['output'], 'test output 2')
            self.assertEqual(prompt.examples[0]['type'], 'text')

            mock_validate_examples.assert_called_once()

    def test_update_2(self):
        # ensure that examples can't be updated
        # when template_params are updated

        prompt_data = self.prompt_data.copy()
        prompt_data['examples'] = [self.output1.id, self.output2.id]
        prompt_data['template_params'] = [{
            "name": "prompt",
            "description": "Being updated"
        }]
        serializer = DummyPromptSellerSerializer(
            instance=self.prompt,
            data=prompt_data,  # type:ignore
            context={'request': self.serializer.context['request']}
        )
        self.assertTrue(serializer.is_valid())
        prompt = serializer.save()
        self.assertEqual(prompt.examples, None)


class DummyPromptBuyerSerializer(AbstractPromptBuyerSerializer):
    class Meta(AbstractPromptBuyerSerializer.Meta):
        model = GPT3PromptModel


class BadModelDummyPromptBuyerSerializer(AbstractPromptBuyerSerializer):
    """ Uses an invalid model in Meta class"""
    class Meta(AbstractPromptBuyerSerializer.Meta):
        model = User


class AbstractPromptBuyerSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(  # type:ignore
            email='testuser@email.com',
            username='testuser',
            password='testpassword')
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
        self.prompt = GPT3PromptModel.objects.create(
            **self.prompt_data
        )

        request = type('Request', (object,), {
            'user': self.user
        })
        self.serializer = DummyPromptBuyerSerializer(
            context={'request': request},
            instance=self.prompt
        )

    def test_init_subclass(self):
        # ensure model is of AbstractPromptModel
        with self.assertRaises(AssertionError) as context:
            BadModelDummyPromptBuyerSerializer(
                instance=self.prompt,
                data=self.prompt_params  # type: ignore
            )

        self.assertTrue(
            "model must be a subclass of AbstractPromptModel"
            in str(context.exception)
        )

    def test_init_instance(self):
        # ensure instance is set
        with self.assertRaises(AssertionError) as context:
            DummyPromptBuyerSerializer(
                instance=None,
                data=self.prompt_params  # type: ignore
            )

        self.assertTrue(
            "instance must be set during initialization"
            in str(context.exception)
        )

    def test_fields(self):
        # ensure that all AbstractPromptBuyerSerializer
        # fields are included in the serializer
        self.assertEqual(
            set(AbstractPromptBuyerSerializer.Meta.fields),
            set(self.serializer.fields.keys())
        )

    def test_validate_prompt_params(self):
        # ensure that prompt_params are validated
        # by the model
        self.prompt.validate_prompt = mock.Mock()
        self.prompt.validate_prompt.return_value = True
        self.serializer.validate_prompt_params(self.prompt_params)
        self.prompt.validate_prompt.assert_called_once()

    def test_validate_prompt_params_2(self):
        # ensure that prompt_params are validated
        # when a serializer is created
        self.prompt.validate_prompt = mock.Mock()
        self.prompt.validate_prompt.return_value = True
        serializer = DummyPromptBuyerSerializer(
            instance=self.prompt,
            data={
                'prompt_params': self.prompt_params,
            },  # type: ignore
            context={'request': self.serializer.context['request']}
        )
        serializer.is_valid(raise_exception=True)
        self.assertTrue(serializer.is_valid())
        self.prompt.validate_prompt.assert_called_once()

    # def test_generate(self):
    #     # ensure that generate method is implemented
    #     with self.assertRaises(NotImplementedError):
    #         self.serializer.generate()
