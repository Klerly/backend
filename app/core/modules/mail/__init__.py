import mailchimp_transactional
from mailchimp_transactional.api_client import ApiClientError
from django.conf import settings
import logging
import abc


class AbstractMail(abc.ABC):
    """
    Abstract base class for sending emails using a specific mail API.
    """

    def __init__(self, key: str):
        """
        Constructor for the AbstractMail class.

        Args:
            key (str): The API key for the mail API.
        """
        if not key:
            raise ValueError("No Mail API key provided")
        self.key = key

    @abc.abstractmethod
    def send(self, to, subject, text, html=None) -> bool:
        """
        Send an email using the mail API.

        Args:
            to (str): The recipient email address.
            subject (str): The subject line of the email.
            text (str): The plain text message body of the email.
            html (str, optional): The HTML message body of the email.

        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
        raise NotImplementedError


class MailChimp(AbstractMail):
    """
    Concrete subclass of AbstractMail that sends emails using the MailChimp Transactional Email API.
    """

    def __init__(self):
        """
        Constructor for the MailChimp class.
        """
        # Get the MailChimp API key from Django settings
        key = getattr(settings, 'MAILCHIMP_API_KEY', "")
        # Call the parent class constructor
        super().__init__(key)
        # Create a new MailchimpTransactional.Client instance using the API key
        self.mailchimp = mailchimp_transactional.Client(key)

    def send(self, to, subject, text, html=None):
        """
        Send an email using the MailChimp Transactional Email API.

        Args:
            to (str): The recipient email address.
            subject (str): The subject line of the email.
            text (str): The plain text message body of the email.
            html (str, optional): The HTML message body of the email.

        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
        # Create a new message using the provided parameters
        message = {
            "from_email": getattr(settings, 'DEFAULT_FROM_EMAIL', " "),
            "subject": subject,
            "text": text,
            "to": [
                {
                    "email": to,
                    "type": "to"
                }
            ]
        }

        if html:
            message["html"] = html

        try:
            self.mailchimp.messages.send({"message": message})
            return True
        except ApiClientError as error:
            logging.error("Mailchimp error:", error.text)
            return False


class Mail:
    """
    Class for sending emails using a specific mail API provider.
    """

    def __init__(self, to, subject, text, html, provider=None):
        """
        Constructor for the Mail class.

        Args:
        to (str): The recipient email address.
            subject (str): The subject line of the email.
            text (str): The plain text message body of the email.
            html (str, optional): The HTML message body of the email.
            provider: (AbstractMail, optional): The mail API provider to use. Defaults to None.
        """
        # Set the mail API provider to use
        self.to = to
        self.subject = subject
        self.text = text
        self.html = html
        self.provider = provider or MailChimp()

    def send(self) -> bool:
        """
        Send an email using the configured mail API provider.

        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
        # Use the send method of the configured
        # mail API provider to send the email

        # only send real emails in production
        if settings.DEBUG:
            print(
                f"Sending fake email to {self.to} with subject {self.subject}"
            )
            return True

        return self.provider.send(self.to, self.subject, self.text, self.html)
