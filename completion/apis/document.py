from rest_framework import generics
from rest_framework.views import APIView
from completion.models import DocumentModel
from completion.serializers import DocumentListCreateSerializer, DocumentRetrieveUpdateDestroySerializer
from core.response import SuccessResponse
from rest_framework.exceptions import PermissionDenied
from core.exceptions import HttpValidationError


class DocumentListCreateAPI(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating documents.

    This API endpoint allows authenticated users to list all the documents
    that they have created, or to create a new document by sending a POST
    request with the required data.
    """

    serializer_class = DocumentListCreateSerializer

    def get_queryset(self):
        return DocumentModel.objects.filter(user=self.request.user)


class DocumentRetrieveUpdateDestroyAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting documents.

    This API endpoint allows authenticated users to retrieve, update, or
    delete a document by sending a GET, PUT, or DELETE request to the
    appropriate URL.
    """

    serializer_class = DocumentRetrieveUpdateDestroySerializer

    def get_queryset(self):
        return DocumentModel.objects.filter(user=self.request.user)


class DocumentCompleteAPI(APIView):
    """
    API endpoint for completing a document.

    This API endpoint allows authenticated users to complete a document by
    sending a POST request with the required data.
    """

    def post(self, request, pk):
        """
        Custom method to handle POST requests.

        This method receives the text to be added to the document, calls the
        `complete` method of the `DocumentModel` object, and returns the
        completed text.
        """
        try:
            document = DocumentModel.objects.get(pk=pk)
        except DocumentModel.DoesNotExist:
            return HttpValidationError('Invalid document id')

        if request.user != document.user:
            return PermissionDenied()

        new_text = request.data.get('text')
        if not new_text:
            return HttpValidationError({'text': 'Missing text'})

        return SuccessResponse({'text': document.complete(new_text)})
