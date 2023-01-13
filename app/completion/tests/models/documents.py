from django.test import TestCase
from django.utils import timezone
from model_bakery import baker
from unittest.mock import patch

from account.models import User
from completion.models import DocumentModel, PromptModel, CompletionModel


class DocumentModelTestCase(TestCase):
    def setUp(self):
        self.user: User = User.objects.create_user(  # type: ignore
            username='test@example.com',
            email='test@example.com',
            password='testpass'
        )
        self.prompt: PromptModel = PromptModel.objects.create(
            heading='Test Prompt',
            image='https://example.com/image.jpg',
            description='Test description',
            prompt='Test prompt: '
        )
        self.document: DocumentModel = baker.make(
            DocumentModel,
            user=self.user,
            prompt=self.prompt,
            name='Test Document',
            text='Test text'
        )

    def test_complete(self):

        with patch('openai.Completion.create') as mock_create:
            mock_create.return_value = {
                'id': 'test-id',
                'object': 'text_completion',
                'created': 1626119515,
                'model': 'text-davinci-003',
                'choices': [{
                    'text': 'Some newly generated text',
                }]
            }

            text = ' This is some new text'
            res_text = self.document.complete(text)

            self.assertEqual(CompletionModel.objects.count(), 1)
            completion: CompletionModel = CompletionModel.objects.first()  # type: ignore

            self.assertEqual(completion.uid, 'test-id')
            self.assertEqual(completion.input, self.prompt.prompt + text)
            self.assertEqual(completion.output, res_text)
            self.assertEqual(completion.user, self.user)
