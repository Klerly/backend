from rest_framework import serializers
from jarvis.models import (
    AbstractPromptModel,
    PromptOutputModel
)
from typing import List, Type, Dict, Union,Any
from account.models import User, Seller
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.fields import empty
from jarvis.serializers.output import PromptOutputSerializer
from account.serializers.user import PublicSellerSerializer

class AbstractPromptSellerSerializer(serializers.ModelSerializer):
    is_seller_active = serializers.SerializerMethodField()
    template_params = serializers.JSONField(
        required=False,
        default=[],
    )
    class Meta:
        model: Type[AbstractPromptModel] = None  # type: ignore
        # type: ignore
        output_model: Type[PromptOutputModel] = PromptOutputModel
        read_only_fields = (
            'id',
            'created_at',
            'updated_at',
            'is_active',
            'is_seller_active',
            'name'
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

    def __init__(self, instance=None, data=empty, **kwargs):
        if not self.Meta.model:
            raise AssertionError(
                "model must be set in the Meta class"
            )
        if not issubclass(self.Meta.model, AbstractPromptModel):
            raise AssertionError(
                "model must be a subclass of AbstractPromptModel"
            )

        super().__init__(instance, data, **kwargs)

    def get_is_seller_active(self, obj):
        return obj.user.seller_profile.is_active

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

        prompt_outputs: List[Type[PromptOutputModel]] = self.Meta.output_model.objects.filter(
            user=self.context['request'].user,
            model_name=self.instance.name,
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
        user: User = self.context['request'].user
        if not user.is_seller():
            raise serializers.ValidationError(
                "You must have a seller profile to create prompts"
            )
        validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # reset the examples if template params are changed
        if 'template_params' in validated_data and validated_data['template_params'] != instance.template_params:
            validated_data['examples'] = None

        return super().update(instance, validated_data)


class AbstractPromptBuyerSerializer(serializers.ModelSerializer):
    seller = serializers.SerializerMethodField()
    prompt_params = serializers.JSONField(
        required=False,
        write_only=True
    )

    class Meta:
        model = AbstractPromptModel
        read_only_fields = (
            'id',
            'heading',
            'name',
            'description',
            'created_at',
            'updated_at',
            'icon',
            'type',
            'examples',
            'seller',
            'template_params',

        )
        fields = read_only_fields + (
            "prompt_params",
        )

        restricted_fields = (
            'template',
        )

    # check that there is an instance
    # check that the instance is valid

    def __init__(self, instance=None, data=empty, **kwargs):
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

        if not instance and data is not empty:
            raise AssertionError(
                "instance must be set during initialization"
            )

        # check that the read only fields in any subclasses
        # are a subset of the read only fields in the base class.

        if not set(self.Meta.read_only_fields).issubset(set(AbstractPromptBuyerSerializer.Meta.read_only_fields)):
            raise AssertionError(
                """
                read_only_fields must be a subset of the read_only_fields in the base class

                To solve this issue, add the following to the Meta class:

                read_only_fields = AbstractPromptBuyerSerializer.Meta.read_only_fields + (
                    "your_read_only_field",
                )
                """
            )

        # check that the restricted fields do not appear in the fields
        if set(self.Meta.restricted_fields).intersection(set(self.Meta.fields)):
            raise AssertionError(
                """
                restricted_fields must not appear in the fields list

                 To solve this issue, remove the following from the {} Meta class:

                "{}"
                """.format(
                    self.__class__.__name__,
                    ", ".join(self.Meta.restricted_fields)
                )
            )

        super().__init__(instance, data, **kwargs)

    def get_seller(self, obj: AbstractPromptModel):
        seller: Seller = obj.user.seller_profile
        return PublicSellerSerializer(seller).data

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

    def generate(self) -> Dict[str, Any]:
        """ Generate a prompt output
        """
        instance: AbstractPromptModel = self.instance  # type: ignore
        prompt_params: Dict[str, Union[str, int]] = {}
        if self.validated_data:
            prompt_params = self.validated_data.pop(  # type: ignore
                'prompt_params', {}) or {}
        user = self.context['request'].user
        outputModel = instance.generate(
            user,
            **prompt_params,
            **self.validated_data
        )
        return PromptOutputSerializer(outputModel).data


    def create(self, validated_data):
        """ This should never be called"""
        raise NotImplementedError

    def update(self, instance, validated_data):
        """ This should never be called"""
        raise NotImplementedError
