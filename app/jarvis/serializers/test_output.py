from jarvis.models import (
    PromptOutputModel
)
from jarvis.models.abstract import AbstractPromptModel
from jarvis.serializers import PromptOutputSerializer
from account.serializers.user import PublicSellerSerializer

from django.test import TestCase
from jarvis.models import PromptOutputModel
from account.models import User, Seller
from unittest import mock


class TestRestrictedSerializer(PromptOutputSerializer):
    class Meta(PromptOutputSerializer.Meta):
        fields = PromptOutputSerializer.Meta.read_only_fields + (
            "model_input",
            "model_snapshot"
        )


class PromptOutputSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(  # type:ignore
            email='testuser@email.com',
            username='testuser',
            password='testpassword'
        )
        self.seller = Seller.objects.create(  # type:ignore
            user=self.user,
            name='test seller',
            handle='testseller',
            about='test description',
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
            model_snapshot={"description": "test description"}
        )
        self.request = type('Request', (object,), {
            'user': self.user
        })

    def test_restricted_fields(self):
        with self.assertRaises(AssertionError) as context:
            TestRestrictedSerializer()

        self.assertTrue(
            'restricted_fields must not appear in the fields list' in str(
                context.exception)
        )

    def test_output_serializer(self):
        serializer = PromptOutputSerializer(
            self.output, context={'request': self.request})
        self.assertEqual(serializer.data['id'], self.output.id)  # type: ignore
        self.assertEqual(serializer.data['input'], self.output.input)
        self.assertEqual(serializer.data['output'], self.output.output)
        self.assertEqual(serializer.data['cost'], self.output.cost)
        self.assertEqual(serializer.data['model_name'], self.output.model_name)
        self.assertEqual(serializer.data['type'], self.output.type)
        self.assertEqual(
            serializer.data['seller'],
            PublicSellerSerializer(self.seller).data
        )
