from django.test import TestCase
from jarvis.models import (
    Dalle2PromptModel,
    Dalle2PromptOutputModel
)
from account.models import User
from unittest.mock import patch


class Dalle2PromptModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(  # type: ignore
            username="testuser",
            email="testuser@email.co",
            password="testpassword"
        )
        self.concrete_model = Dalle2PromptModel
        self.prompt: Dalle2PromptModel = self.concrete_model.objects.create(
            icon="https://www.google.com",
            heading="Sample Heading",
            description="Sample Description",
            template="""
             A logo for a business that does {business_type} and the name of the business is {business_name}
             . The logo should be simple and memorable. It should also be in the form of an acronym.
            """,
            template_params=[
                {
                    "name": "business_name",
                    "description": "The name of the business"
                },
                {
                    "name": "business_type",
                    "description": "The type of business"
                }
            ],
            user=self.user
        )

    def test_create(self):
        self.assertEqual(self.concrete_model.objects.count(), 1)

    def test_complete(self):
        with patch(
            "openai.Image.create",
            return_value={
                "created": 1674592929,
                "data": [
                {
                    "url": "https://oaidalleapiprodscus.blob.core.windows.net/private/org-j9eOajUvLxeTO860Y55ik3kt/user-GE0lNHcWJfexX4mjlJF0jf3j/img-NGqjuEX1VOIYXb5BdmEv8NND.png?st=2023-01-24T19%3A42%3A09Z&se=2023-01-24T21%3A42%3A09Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-01-24T18%3A08%3A20Z&ske=2023-01-25T18%3A08%3A20Z&sks=b&skv=2021-08-06&sig=KdMiIMTp9zMltwSxwGNhs2U%2BuTgSbmfOnQvMRDqN4ss%3D"
                }
                ]
            }

        ) as mock:

            self.prompt.generate(
                size="256x256",
                business_name="Vitamin Group",
                business_type="provide vitamin supplements"
            )
            mock.assert_called_once_with(
                size="256x256",
                user=str(self.user.id),
                prompt=self.prompt.get_prompt(
                    business_name="Vitamin Group",
                    business_type="provide vitamin supplements"
                ),
                response_format="url",  # or "b64_json"
                n=1
            )

            self.assertEqual(Dalle2PromptOutputModel.objects.count(), 1)

    def test_delete(self):
        self.assertEqual(
            self.concrete_model.objects.first().is_active,  # type: ignore
            1
        )
        self.prompt.delete()
        self.assertEqual(
            self.concrete_model.objects.first().is_active,  # type: ignore
            0
        )
