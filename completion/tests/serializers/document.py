from django.test import TestCase

from completion.models import DocumentModel, PromptModel
from completion.serializers import DocumentListCreateSerializer, DocumentRetrieveUpdateDestroySerializer
from account.models import User
from core.exceptions import HttpValidationError
from rest_framework import serializers


class DocumentListCreateSerializerTestCase(TestCase):
    def setUp(self):
        self.prompt = PromptModel.objects.create(
            heading='Test Prompt',
            image='https://example.com/image.jpg',
            description='Test description',
            prompt='Test prompt'
        )
        self.user = User.objects.create_user(  # type: ignore
            username='test@example.com',
            email='test@example.com',
            password='testpass'
        )
        self.context = {'request': {'user': self.user}}

        class MockRequest:
            user = self.user

        self.context = {'request': MockRequest()}

    def test_valid_data(self):
        data = {
            'name': 'Test Document',
            'text': 'Test text',
            'prompt_id': self.prompt.id
        }
        serializer = DocumentListCreateSerializer(
            data=data,  # type: ignore
            context=self.context
        )
        self.assertTrue(serializer.is_valid())
        document = serializer.save()
        self.assertEqual(document.name, 'Test Document')
        self.assertEqual(document.text, 'Test text')
        self.assertEqual(document.prompt, self.prompt)
        self.assertEqual(document.user, self.user)

    def test_missing_required_field(self):
        data = {
            'name': 'Test text',
            'prompt_id': self.prompt.id,
            'text': 'Test text',
        }

        for field in ['name', 'text', 'prompt_id']:
            data_copy = data.copy()
            data_copy.pop(field)
            serializer = DocumentListCreateSerializer(
                data=data_copy,  # type: ignore
                context=self.context
            )
            self.assertFalse(serializer.is_valid())
            self.assertEqual(serializer.errors, {
                             field: ['This field is required.']})

    def test_invalid_prompt_id(self):
        data = {
            'name': 'Test Document',
            'text': 'Test text',
            'prompt_id': 9999999999
        }
        serializer = DocumentListCreateSerializer(
            data=data, context=self.context)  # type: ignore
        self.assertTrue(serializer.is_valid())
        with self.assertRaises(HttpValidationError):
            serializer.save()

    def test_excluded_prompt(self):
        """ Ensure that the prompt field is 
            excluded from the serializer response
        """

        document = DocumentModel.objects.create(
            name='Test Document',
            text='Test text',
            prompt=self.prompt,
            user=self.user
        )
        serializer = DocumentListCreateSerializer(
            document, context=self.context)
        self.assertNotIn('prompt', serializer.data)


class DocumentRetrieveUpdateDestroySerializerTestCase(TestCase):
    def setUp(self):
        self.prompt = PromptModel.objects.create(
            heading='Test Prompt',
            image='https://example.com/image.jpg',
            description='Test description',
            prompt='Test prompt'
        )
        self.user = User.objects.create_user(  # type: ignore
            username='test@example.com',
            email='test@example.com',
            password='testpass'
        )
        self.context = {'request': {'user': self.user}}

        class MockRequest:
            user = self.user

        self.context = {'request': MockRequest()}

    def test_valid_data(self):
        instance: DocumentModel = DocumentModel.objects.create(
            name='Test Document',
            text='Test text',
            prompt=self.prompt,
            user=self.user
        )
        serializer = DocumentRetrieveUpdateDestroySerializer(
            instance, data={'text': 'new text'}, partial=True  # type: ignore
        )

        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(serializer.data["name"], 'Test Document')
        self.assertEqual(serializer.data["text"], 'new text')
