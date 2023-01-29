
from core.models import BaseModel
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from jarvis.models.abstract import AbstractPromptModel


class PromptOutputModel(BaseModel):
    uid = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    """ Unique id from the provider e.g. a 
        unique id from the gpt3 open ai's api
     """

    input = models.JSONField(
        null=True,
        blank=True
    )
    """ User input JSON without the template
        E.g. {
            "name": "John Doe", 
            "age": 20
            }
    """

    output = models.TextField()
    """ Output from the model
        E.g. "Hello John Doe, you are 20 years old"
        or "https://example.com/image.png"
    """

    type = models.CharField(
        max_length=255,
        choices=AbstractPromptModel.Types.choices)
    """ Type of the prompt e.g text or image"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.DO_NOTHING,
                             related_name="prompt_outputs",
                             )

    cost = models.FloatField()
    """ Total cost of generating prompt output """

    model_name = models.CharField(
        max_length=255,
        choices=AbstractPromptModel.Names.choices
    )
    """ Name of the model used to generate the output 
        e.g. gpt3, dalle2
    """

    model_input = models.TextField()
    """ Input to the model including the template
        E.g. "Write a paragraph about John Doe who is 20 years old"
        where the template is "Write a paragraph about {name} who is {age} years old"
    """
    model_snapshot = models.JSONField()
    """ JSON snapshot of the model used to generate the output
        i.e model.__dict__
        E.g. {
            "name": "gpt3",
            "type": "text",   
            "template": "Write a paragraph about {name} who is {age} years old",
            "template_params": [
                {
                    "name": "name",
                    "description": "Name of the person",
                },
                ...
            ],
            "examples": None,
            "user": 1,
            ...
        }
"""

    class Meta:
        verbose_name = _('Prompt Output')
        verbose_name_plural = _('Prompt Outputs')
        ordering = ('-created_at',)

    def __str__(self):
        return "{} - {}".format(self.user, self.uid)
