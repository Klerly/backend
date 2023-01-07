from rest_framework import serializers
from completion.models import DocumentModel, PromptModel
from core.exceptions import HttpValidationError


class DocumentListCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for the DocumentModel model.

    This serializer is used to convert the DocumentModel model instances
    into JSON format for the API responses.
    """

    prompt_id = serializers.IntegerField(
        required=True,
        write_only=True,
        help_text='The id of the prompt associated with the document.'
    )

    class Meta:
        model = DocumentModel
        fields = (
            'name',
            'text',
            'created_at',
            'updated_at',
            'prompt_id'
        )

    def create(self, validated_data):
        """
        Custom create method for the DocumentListCreateSerializer.

        This method is used to create a new DocumentModel instance and
        associate it with a PromptModel instance. The user field is
        also set to the current user.
        """
        user = self.context['request'].user
        validated_data['user'] = user
        prompt_id = validated_data.pop('prompt_id')
        try:
            prompt = PromptModel.objects.get(pk=prompt_id)
        except PromptModel.DoesNotExist:
            raise HttpValidationError({
                'prompt_id': 'Invalid prompt id'
            })
        validated_data['prompt'] = prompt
        return super().create(validated_data)


class DocumentRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    """
    Serializer for the DocumentModel model.

    This serializer is used to convert the DocumentModel model instances
    into JSON format for the API responses.
    """
    name = serializers.CharField(required=False)
    text = serializers.CharField(required=False)

    class Meta:
        model = DocumentModel
        fields = (
            'name',
            'text',
            'created_at',
            'updated_at'
        )
