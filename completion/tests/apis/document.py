from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from account.models import User
from completion.models import DocumentModel, PromptModel
from completion.serializers import DocumentListCreateSerializer, DocumentRetrieveUpdateDestroySerializer


class DocumentListCreateAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
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
        self.client.force_authenticate(user=self.user)
        self.url = reverse('completion:document-list')

    def test_serializer_class(self):
        """ Test that the serializer class for the API is the expected class """
        from completion.apis import DocumentListCreateAPI
        api_view = DocumentListCreateAPI()
        self.assertEqual(api_view.serializer_class,
                         DocumentListCreateSerializer)

    def test_create_document(self):
        """ Test creating a new document """
        data = {
            'name': 'Test Document',
            'text': 'This is a test document',
            'prompt_id': self.prompt.id
        }
        response = self.client.post(
            self.url,
            data,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(DocumentModel.objects.count(), 1)
        self.assertEqual(DocumentModel.objects.get().name, 'Test Document')

    def test_list_documents(self):
        """ Test listing all documents for a user """
        DocumentModel.objects.create(
            user=self.user,
            prompt=self.prompt,
            name='Test Document 1',
            text='This is a test document'
        )
        DocumentModel.objects.create(
            user=self.user,
            prompt=self.prompt,
            name='Test Document 2',
            text='This is a test document'
        )

        # third document is for a different user
        # should not be returned in the list
        DocumentModel.objects.create(
            user=User.objects.create_user(  # type: ignore
                username='test3@example.com',
                email='test3@example.com',
                password='testpass'
            ),
            prompt=self.prompt,
            name='Test Document 3',
            text='This is a test document'
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.data),  # type: ignore
            2
        )


class DocumentRetrieveUpdateDestroyAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
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
        self.client.force_authenticate(user=self.user)
        self.url = reverse('completion:document-retrieve',
                           kwargs={'pk': 1}
                           )

    def test_serializer_class(self):
        """ Test that the serializer class for the API is the expected class """
        from completion.apis import DocumentRetrieveUpdateDestroyAPI
        api_view = DocumentRetrieveUpdateDestroyAPI()
        self.assertEqual(api_view.serializer_class,
                         DocumentRetrieveUpdateDestroySerializer)

    def test_retrieve_document(self):
        """ Test retrieving a document """
        document = DocumentModel.objects.create(
            user=self.user,
            prompt=self.prompt,
            name='Test Document',
            text='This is a test document'
        )
        self.url = reverse('completion:document-retrieve',
                           kwargs={'pk': document.id}
                           )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'],  # type: ignore
                         'Test Document')

    def test_update_document(self):
        """ Test updating a document """
        document = DocumentModel.objects.create(
            user=self.user,
            prompt=self.prompt,
            name='Test Document',
            text='This is a test document'
        )
        self.url = reverse('completion:document-retrieve',
                           kwargs={'pk': document.id}
                           )
        data = {
            'name': 'Test Document Updated',
            'text': 'This is a test document updated'
        }
        response = self.client.put(
            self.url,
            data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'],  # type: ignore
                         'Test Document Updated')

    def test_delete_document(self):
        """ Test deleting a document """
        document = DocumentModel.objects.create(
            user=self.user,
            prompt=self.prompt,
            name='Test Document',
            text='This is a test document'
        )
        self.url = reverse('completion:document-retrieve',
                           kwargs={'pk': document.id}
                           )
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(DocumentModel.objects.count(), 0)
