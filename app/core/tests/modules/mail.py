
from django.test import TestCase
from core.modules.mail import AbstractMail, MailChimp, Mail
from unittest.mock import Mock, patch
from mailchimp_transactional.api_client import ApiClientError
from django.conf import settings
import logging


class TestAbstractMail(TestCase):
    def test_send_method(self):
        # Create a dummy subclass of AbstractMail that always returns True
        class DummyMail(AbstractMail):
            def send(self, to, subject, text, html=None):
                return True

        # Create a new DummyMail instance
        mail = DummyMail("dummy_key")
        # Test that the send method returns True
        self.assertTrue(mail.send("to@example.com", "subject", "text"))

    def test_send_method_with_html(self):
        # Create a dummy subclass of AbstractMail that always returns True
        class DummyMail(AbstractMail):
            def send(self, to, subject, text, html=None):
                return True

        # Create a new DummyMail instance
        mail = DummyMail("dummy_key")
        # Test that the send method returns True when given an HTML message body
        self.assertTrue(mail.send("to@example.com",
                        "subject", "text", "<p>html</p>"))


class MailChimpTestCase(TestCase):
    def test_send_success(self):
        mock_send = Mock(return_value=True)
        mock_mailchimp_client = Mock()
        mock_mailchimp_client.messages.send = mock_send

        mail = MailChimp()
        mail.mailchimp = mock_mailchimp_client

        result = mail.send('to@example.com', 'subject', 'text')
        self.assertTrue(result)
        mock_mailchimp_client.messages.send.assert_called_with(
            {'message': {'from_email': settings.DEFAULT_FROM_EMAIL, 'subject': 'subject',
                         'text': 'text', 'to': [{'email': 'to@example.com', 'type': 'to'}]}}
        )

    def test_send_failure(self):
        with patch.object(logging, 'error', side_effect=None):
            mock_mailchimp_client = Mock()
            mock_mailchimp_client.messages.send.side_effect = ApiClientError(
                "test", 400
            )
            mailchimp = MailChimp()
            mailchimp.mailchimp = mock_mailchimp_client
            result = mailchimp.send("to@example.com", "subject", "text")
            self.assertFalse(result)


class MailTestCase(TestCase):
    def setUp(self):
        self.to = "to@example.com"
        self.subject = "subject"
        self.text = "text"
        self.html = "html"

    @patch.object(MailChimp, "send")
    def test_send_success(self, mock_send):
        # Test that the Mail class sends the email using the MailChimp API
        # and returns True if the send method of the MailChimp API returns True
        mock_send.return_value = True
        mail = Mail(self.to, self.subject, self.text, self.html)
        self.assertTrue(mail.send())
        mock_send.assert_called_with(
            self.to, self.subject, self.text, self.html)

    @patch.object(MailChimp, "send")
    def test_send_failure(self, mock_send):
        # Test that the Mail class sends the email using the MailChimp API
        # and returns False if the send method of the MailChimp API returns False
        mock_send.return_value = False
        mail = Mail(self.to, self.subject, self.text, self.html)
        self.assertFalse(mail.send())
        mock_send.assert_called_with(
            self.to, self.subject, self.text, self.html)
