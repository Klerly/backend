# from jarvis.models import AbstractPromptModel, CompletionModel
from django.test import TestCase
from jarvis.models import (
    GPT3PromptModel
)
from account.models import User,Seller
from rest_framework.exceptions import ValidationError
from unittest.mock import patch


class AbstractPromptModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(  # type: ignore
            username="testuser",
            email="testuser@email.co",
            password="testpassword"
        )
        self.seller: Seller = Seller.objects.create(  # type: ignore
            user=self.user,
            handle='testhandle',
            name='Test Name',
        )
        self.concrete_model = GPT3PromptModel

        self.prompt_data = {
            "icon": "https://www.google.com",
            "heading": "Sample Heading",
            "description": "Sample Description",
            "template": """
            This is a sample template
            Generate a business name acronym: {business_name}
            I am into {business_type} and I need a name for my business
            """,
            "template_params": [
                {
                    "name": "business_name",
                    "description": "The name of the business"
                },
                {
                    "name": "business_type",
                    "description": "The type of business"
                }
            ],
            "user": self.user
        }

        self.prompt = self.concrete_model.objects.create(
            **self.prompt_data
        )

    def test_create(self):
        with patch.object(
            self.concrete_model, "validate_template"
        ) as mockvalidate_template_params, patch.object(
            self.concrete_model, "_validate_example"
        ) as mock_validate_example:
            self.concrete_model.objects.create(
                **self.prompt_data
            )
            mockvalidate_template_params.assert_called_once()
            mock_validate_example.assert_called_once()

    def test_create_invalid_template(self):
        with self.assertRaises(ValidationError) as context:
            self.concrete_model.objects.create(
                icon="https://www.google.com",
                heading="Sample Heading",
                description="Sample Description",
                template="""
                This is a sample template
                Generate a business name acronym: {business_name}
                I am into {business_type} and I need a name for my business
                """,
                template_params=[
                    {
                        "name": "business_name",
                        "description": "The name of the business"
                    },
                    {
                        "description": "The type of business"
                    }
                ],
                user=self.user
            )
        self.assertTrue(
            "The template parameter is missing the \"name\" key" in str(
                context.exception)
        )

    def test_create_invalid_template_2(self):
        with self.assertRaises(ValidationError) as context:
            self.concrete_model.objects.create(
                icon="https://www.google.com",
                heading="Sample Heading",
                description="Sample Description",
                template="""
                This is a sample template
                Generate a business name acronym: {business_name}
                I am into {business_type} and I need a name for my business
                """,
                template_params=[
                    {
                        "name": "business_name",
                        "description": "The name of the business"
                    },
                    {
                        "name": "business_type",
                    }
                ],

                user=self.user
            )
        self.assertTrue(
            "The template parameter is missing the \"description\" key" in str(
                context.exception)
        )

    def test_create_invalid_template_3(self):
        with self.assertRaises(ValidationError) as context:
            self.concrete_model.objects.create(
                icon="https://www.google.com",
                heading="Sample Heading",
                description="Sample Description",
                # it fails because of the invalid whitespace in the template
                template="""
                This is a sample template
                Generate a business name acronym: {business_name}
                I am into { business_type } and I need a name for my business
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
        self.assertTrue(
            "The template parameter \" business_type \" has an invalid white space" in str(
                context.exception)
        )

    def test_create_invalid_template_4(self):
        with self.assertRaises(ValidationError) as context:
            self.concrete_model.objects.create(
                icon="https://www.google.com",
                heading="Sample Heading",
                description="Sample Description",
                template="""
                This is a sample template
                Generate a business name acronym: {business_name}
                I am into x and I need a name for my business
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
        self.assertTrue(
            "The template parameter \"business_type\" is missing" in str(
                context.exception)
        )

    def test_create_invalid_template_5(self):
        with self.assertRaises(ValidationError) as context:
            self.concrete_model.objects.create(
                icon="https://www.google.com",
                heading="Sample Heading",
                description="Sample Description",
                template="""
                This is a sample template
                Generate a business name acronym: {business_name}
                I am into {business_type} {business_type} and I need a name for my business
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
        self.assertTrue(
            "The template parameter \"business_type\" appears more than once in the template" in str(
                context.exception)
        )

    def test_create_invalid_template_6(self):
        with self.assertRaises(ValidationError) as context:
            self.concrete_model.objects.create(
                icon="https://www.google.com",
                heading="Sample Heading",
                description="Sample Description",
                template="""
                This is a sample template
                Generate a business name acronym: {business_name}
                """,
                template_params=[],
                user=self.user
            )
        self.assertTrue(
            "is missing the \"business_name\" key" in str(
                context.exception)
        )

    def test_validate_prompt(self):
        data = {
            "business_name": "Test Business",
            "business_type": "Test Type"
        }
        self.prompt.validate_prompt(**data)

    def test_validate_prompt_invalid(self):
        data = {
            "business_name": "Test Business",
            "business_type": "Test Type",
            "invalid": "Invalid"
        }
        with self.assertRaises(ValidationError) as context:
            self.prompt.validate_prompt(**data)
        self.assertTrue(
            "Invalid number of parameters passed" in str(context.exception)
        )

    def test_validate_prompt_invalid_2(self):
        data = {
            "business_name": "Test Business",
            "invalid": "Invalid"
        }
        with self.assertRaises(ValidationError) as context:
            self.prompt.validate_prompt(**data)
        self.assertTrue(
            "Invalid parameter passed" in str(context.exception)
        )

    def test_validate_example(self):
        self.prompt.examples = [
            {
                "params": {
                    "business_name": "Test Business",
                    "business_type": "Test Type"
                },
                "output": "Test Business",
                "type": "text"
            },
            {
                "params": {
                    "business_name": "Another name",
                    "business_type": "Another type"
                },
                "output": "Test Business",
                "type": "text"
            }
        ]
        self.prompt._validate_example()
        # expects no error

        self.prompt.examples = None
        self.prompt._validate_example()
        # expects no error

    def test_validate_example_invalid(self):
        self.prompt.examples = [
            {
                "params": {
                    "business_name": "Test Business",
                    "unknown_key": "Test Type"
                },
                "output": "Test Business",
                "type": "text"
            },
            {
                "params": {
                    "business_name": "Another name",
                    "unknown_key": "Another type"
                },
                "output": "Test Business",
                "type": "text"
            }
        ]
        with self.assertRaises(ValidationError) as context:
            self.prompt._validate_example()
        self.assertTrue(
            "All examples must have the same keys as the template params" in str(
                context.exception)
        )

    def test_validate_example_invalid_2(self):
        self.prompt.examples = [
            {
                "params": {
                    "business_name": "Test Business",
                    "business_type": "Test Type"
                },
                "output": "Test Business",
                "type": "text"
            },
            {
                "params": {
                    "business_name": "Another name",
                    "unknown_key": "Another type"
                },
                "output": "Test Business",
                "type": "text"
            }
        ]
        with self.assertRaises(ValidationError) as context:
            self.prompt._validate_example()
        self.assertTrue(
            "All examples must have the same keys" in str(
                context.exception)
        )

    def test_validate_example_invalid_3(self):
        self.prompt.examples = [
            {
                "params": {
                    "business_name": "Test Business",
                    "business_type": "Test Type"
                },
                "output": "Test Business",
            },
            {
                "params": {
                    "business_name": "Another name",
                    "business_type": "Another type"
                },
                "output": "Test Business",
                "type": "text"
            }
        ]
        with self.assertRaises(ValidationError) as context:
            self.prompt._validate_example()
        self.assertTrue(
            "All examples must have the keys 'params', 'output' and 'type'" in str(
                context.exception)
        )

    def test_validate_example_invalid_4(self):
        self.prompt.examples = "invalid"
        with self.assertRaises(ValidationError) as context:
            self.prompt._validate_example()
        self.assertTrue(
            "Examples must be a list" in str(
                context.exception)
        )

    def test_validate_example_invalid_5(self):
        self.prompt.examples = ["invalid"]
        with self.assertRaises(ValidationError) as context:
            self.prompt._validate_example()
        self.assertTrue(
            "Examples must be a list of dicts" in str(
                context.exception)
        )

    def test_get_prompt(self):
        data = {
            "business_name": "Test Business",
            "business_type": "Test Type"
        }
        prompt = self.prompt.get_prompt(**data)
        self.assertEqual(
            prompt, """
            This is a sample template
            Generate a business name acronym: Test Business
            I am into Test Type and I need a name for my business
            """
        )

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
