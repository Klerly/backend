
from django.conf import settings
from core.modules.mail import Mail
from account.models import User
from account.models import EmailTokenVerificationModel, ResetPasswordTokenVerificationModel


class AccountMailTemplate:
    """ Mail template class
    """
    class ResetPassword(Mail):
        """ Template for sending a password reset email.

        Args:
            to (str): The recipient email address.
            first_name (str): The first name of the recipient.
            token (str): The password reset token.

        """

        def __init__(self, user: User):
            token = ResetPasswordTokenVerificationModel.generate_token()
            self.first_name = user.first_name
            self.to = user.email
            self.subject = "Reset your password"
            self.text = """
            Hi {first_name},

            You recently requested to reset your password for your Klerly account. Enter the code below to reset it.

            {token}

            If you didn't request a password reset, please ignore this email or reply to let us know. This password reset is only valid for the next {expiry} hours.

            Thanks,
            The Klerly Team
            """.format(first_name=self.first_name, token=token, expiry=getattr(settings, 'PASSWORD_RESET_TIMEOUT_HOURS'))

            self.html = """
            <html>
            <head></head>
            <body>
            <p>Hi {first_name},</p>
            <p>You recently requested to reset your password for your Klerly account. Enter the code below to reset it.</p>
            <p>{token}</p>
            <p>If you didn't request a password reset, please ignore this email or reply to let us know. This password reset is only valid for the next {expiry} hours.</p>
            <p>Thanks,</p>
            <p>The Klerly Team</p>
            </body>
            </html>
            """.format(first_name=self.first_name, token=token, expiry=getattr(settings, 'PASSWORD_RESET_TIMEOUT_HOURS'))

            super().__init__(self.to, self.subject, self.text, self.html)

            # save the token or rewrite the token if it already exists
            ResetPasswordTokenVerificationModel.objects.update_or_create(
                user=user,
                defaults={
                    'token': token
                }
            )

    class VerifyEmail(Mail):
        """ Template for sending a verification email.

        Args:
            to (str): The recipient email address.
            first_name (str): The first name of the recipient.
            token (str): The verification token.

        """

        def __init__(self, user: User):
            token = EmailTokenVerificationModel.generate_token()
            self.first_name = user.first_name
            self.to = user.email
            self.subject = "Verify your email"
            self.text = """
            Hi {first_name},

            Thanks for signing up for Klerly! We're excited to have you on board.

            Please verify your email address by entering the code below.

            {token}

            If you didn't create an account, please ignore this email or reply to let us know.

            Thanks,
            The Klerly Team
            """.format(first_name=self.first_name, token=token)

            self.html = """
            <html>
            <head></head>
            <body>
            <p>Hi {first_name},</p>
            <p>Thanks for signing up for Klerly! We're excited to have you as an early user.</p>
            <p>Please verify your email address by entering the code below.</p>
            <p>{token}</p>
            <p>If you didn't create an account, please ignore this email or reply to let us know.</p>
            <p>Thanks,</p>
            <p>The Klerly Team</p>
            </body>
            </html>
            """.format(first_name=self.first_name, token=token)

            super().__init__(self.to, self.subject, self.text, self.html)

            # save the token or rewrite the token if it already exists
            EmailTokenVerificationModel.objects.update_or_create(
                user=user,
                defaults={
                    'token': token
                }
            )
