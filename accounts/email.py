# Email helpers for account-related notifications.

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# Render and send an HTML email.
def _send(subject, template, recipient, context):
    # Convert the email template into HTML.
    html = render_to_string(template, context)

    # Create a plain-text version of the email.
    text = strip_tags(html)

    # Send the email using Django's email backend.
    send_mail(
        subject,
        text,
        settings.DEFAULT_FROM_EMAIL,
        [recipient],
        html_message=html,
        fail_silently=False,
    )


# Send an email verification link to the user.
def send_verification_email(user):
    # Get the user's verification token.
    token = user.email_verification_token

    # Send the verification email.
    _send(
        'Verify your email',
        'accounts/emails/verify_email.html',
        user.email,
        {
            # Pass the user object to the template.
            'user': user,

            # Create the verification URL.
            'verify_url': f'{settings.SITE_URL}/accounts/verify-email/{token}/'
            if hasattr(settings, 'SITE_URL') else
            f'/accounts/verify-email/{token}/',
        },
    )


# Send a password reset email.
def send_password_reset_email(user, token):
    # Send the password reset link.
    _send(
        'Reset your password',
        'accounts/emails/reset_password.html',
        user.email,
        {
            # Pass the user object to the template.
            'user': user,

            # Create the password reset URL.
            'reset_url': f'/accounts/reset-password/{token}/',
        },
    )


# Send a welcome email after successful registration.
def send_welcome_email(user):
    # Send the welcome email.
    _send(
        'Welcome to Ecommerence',
        'accounts/emails/welcome.html',
        user.email,
        {'user': user},
    )
