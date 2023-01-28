from rest_framework import serializers
from jarvis.models import (
    AbstractPromptModel,
    AbstractPromptOutputModel
)
from typing import List, Type, Optional


class AbstractPromptSellerSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[AbstractPromptModel] = None  # type: ignore
        output_model: Type[AbstractPromptOutputModel] = None  # type: ignore
        read_only_fields = (
            'id',
            'created_at',
            'updated_at',
        )
        fields = read_only_fields + (
            'icon',
            'heading',
            'description',
            'template',
            'template_params',
            'type',
            'examples',
        )

    def __init__(self, instance=None, data=..., **kwargs):
        if not self.Meta.model:
            raise AssertionError(
                "model must be set in the Meta class"
            )
        if not issubclass(self.Meta.model, AbstractPromptModel):
            raise AssertionError(
                "model must be a subclass of AbstractPromptModel"
            )

        if not self.Meta.output_model:
            raise AssertionError(
                "output_model must be set in the Meta class"
            )
        super().__init__(instance, data, **kwargs)

    def validate_examples(self, value):
        """ Validate the examples field

        Args:
            value (List[int]): The list of prompt output ids

        Raises:
            serializers.ValidationError: If the examples are not valid

        Returns:
            List[Dict[str, Any]]: The list of examples suitable for the model
        """
        if not self.instance:
            raise serializers.ValidationError(
                "Examples can only be added after the prompt is created"
            )

        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Examples must be a list of integers."
            )

        if not all(isinstance(example, int) for example in value):
            raise serializers.ValidationError(
                "Examples must be a list of integers"
            )

        prompt_outputs: List[Type[AbstractPromptOutputModel]] = self.Meta.output_model.objects.filter(
            user=self.context['request'].user,
            model=self.instance,
            id__in=value
        )  # type: ignore

        # check if an example is not found
        if len(prompt_outputs) != len(value):
            raise serializers.ValidationError(
                "One or more examples were not found"
            )

        examples = []
        for output in prompt_outputs:
            examples.append({
                "params": output.input,
                "output": output.output,
                "type": output.type
            })

        return examples

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # reset the examples if template params are changed
        if 'template_params' in validated_data and validated_data['template_params'] != instance.template_params:
            validated_data['examples'] = None

        return super().update(instance, validated_data)


class AbstractPromptBuyerSerializer(serializers.ModelSerializer):
    prompt_params = serializers.JSONField(
        required=True
    )

    class Meta:
        model = AbstractPromptModel
        fields = (
            "prompt_params",
        )

    # check that there is an instance
    # check that the instance is valid

    def __init__(self, instance=None, data=..., **kwargs):
        if not self.Meta.model:
            raise AssertionError(
                "model must be set in the Meta class"
            )

        if not issubclass(self.Meta.model, AbstractPromptModel):
            raise AssertionError(
                "model must be a subclass of AbstractPromptModel"
            )

        # check that model is a subclass of AbstractPromptModel
        if not issubclass(self.Meta.model, AbstractPromptModel):
            raise AssertionError(
                "model must be a subclass of AbstractPromptModel"
            )

        if not instance:
            raise AssertionError(
                "instance must be set during initialization"
            )

        super().__init__(instance, data, **kwargs)

    def validate_prompt_params(self, params: dict):
        """ Validate the prompt field
        """
        if not type(params) is dict:
            raise serializers.ValidationError(
                "Prompt params must be a dictionary"
            )
        instance: AbstractPromptModel = self.instance  # type: ignore
        instance.validate_prompt(**params)
        return params

    def generate(self) -> str:
        """ Generate a prompt output
        """
        raise NotImplementedError

    def create(self, validated_data):
        """ This should never be called"""
        raise NotImplementedError

    def update(self, instance, validated_data):
        """ This should never be called"""
        raise NotImplementedError
