from django.db import models
from core.models import BaseModel
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from jarvis.managers import PromptModelManager
from django.core.exceptions import ObjectDoesNotExist
from account.models import User


class AbstractPromptModel(BaseModel):
    class Names(models.TextChoices):
        GPT3 = 'gpt3', _('GPT3')
        DALLE2 = 'dalle2', _('DALLE2')

    class Types(models.TextChoices):
        TEXT = 'text', _('Text')
        IMAGE = 'image', _('Image')

    objects = PromptModelManager()

    icon = models.URLField(max_length=255, default="https://icon.ico")
    heading = models.CharField(max_length=255)
    description = models.TextField()
    template = models.TextField()
    template_params = models.JSONField()

    examples = models.JSONField(null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name="%(app_label)s_%(class)s_related",
    )

    # To be overridden by subclasses
    type = models.CharField(
        max_length=255,
        choices=Types.choices)

    class Meta:
        verbose_name = _('Prompt')
        verbose_name_plural = _('Prompts')
        ordering = ('-created_at',)
        abstract = True

    def __str__(self):
        return self.heading

    def get_prompt(self, **kwargs):
        from langchain import PromptTemplate
        self.validate_prompt(**kwargs)
        return PromptTemplate(
            input_variables=[param["name"] for param in self.template_params],
            template=self.template
        ).format(**kwargs)

    def _validate_example(self):
        """ Validate the examples the seller has provided

            Raises:
                ValidationError: If the example format is invalid
        """
        if not self.examples:
            return

        # check that it is a list
        if not isinstance(self.examples, list):
            raise ValidationError("Examples must be a list")

        # check that it is a list of dicts
        if not all(isinstance(example, dict) for example in self.examples):  # type: ignore
            raise ValidationError("Examples must be a list of dicts")

        # check that all examples have the required keys
        if not all(
            all(key in example for key in ["params", "output", "type"])
            for example in self.examples  # type: ignore
        ):
            raise ValidationError(
                "All examples must have the keys 'params', 'output' and 'type'"
            )

        # ensure that all examples params have the same keys
        example_params = [example["params"]
                          for example in self.examples]  # type: ignore
        if not all(example_params[0].keys() == example.keys() for example in example_params):
            raise ValidationError("All examples must have the same keys")

        # ensure that all examples params have the same keys as the template params
        template_params_names = [param["name"]
                                 for param in self.template_params]
        # check if items in the list are the same
        if not all(x == y for x, y in zip(example_params[0].keys(), template_params_names)):
            raise ValidationError(
                "All examples must have the same keys as the template params")

    def validate_prompt(self, **kwargs):
        """ Validate that the user input is valid

            Args:
                kwargs (dict): The user input
            Raises:
                ValidationError: If the user input is invalid

        """
        if len(kwargs) != len(self.template_params):
            raise ValidationError("Invalid number of parameters passed")

        for kwarg in kwargs:
            if kwarg not in [param["name"] for param in self.template_params]:
                raise ValidationError(
                    "Invalid parameter passed.\n \"{}\" is not a valid parameter".format(kwarg))

    def validate_template(self):
        for param in self.template_params:
            if "name" not in param:
                raise ValidationError(
                    'The template parameter is missing the "name" key. Ensure that the input has the format {{ "name": "Sample name", "description": "text description" }}'
                )
            if "description" not in param:
                raise ValidationError(
                    'The template parameter is missing the "description" key. Ensure that the input has the format {{ "name": "Sample Name", "description": "text description" }}'
                )

        for param in self.template_params:
            name = param["name"]
            if "{{{}}}".format(name) not in self.template:
                if name in self.template:
                    raise ValidationError(
                        'The template parameter "{}" is missing curly braces. Ensure that the input has the format "{{{}}}"'.format(
                            name, name
                        )
                    )
                else:
                    raise ValidationError(
                        'The template parameter "{}" is missing. Ensure that the input has the format "{{{}}}"'.format(
                            name, name
                        )
                    )
            if self.template.count("{{{}}}".format(name)) > 1:
                raise ValidationError(
                    'The template parameter "{}" appears more than once in the template. Ensure that the parameter appears only once'.format(
                        name
                    )
                )

    def generate(self, **kwargs) -> str:
        """ Generate a prompt from the template and the user input
            Args:
                kwargs (dict): The user input
            Returns:
                str: The generated prompt text or url
        """
        raise NotImplementedError

    def save(self, *args, **kwargs):
        self.validate_template()
        self._validate_example()
        if not self.pk:
            user: User = self.user
            if not user.is_seller():
                raise ValueError(
                    "User with id {} is not a seller".format(user.pk)
                )

        super().save(*args, **kwargs)

