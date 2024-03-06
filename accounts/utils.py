from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_confirmation_email(user_email, token, email_type='confirm'):
    """
    Send an email for account confirmation or password reset.
    :param user_email: Email address of the recipient
    :param token: Confirmation or reset token
    :param email_type: Type of email ('confirm' for account confirmation, 'reset' for password reset)
    """
    if email_type == 'confirm':
        link = f"http://localhost:8000/confirm-email/{token}/"
        subject = 'Confirm Your Email'
        html_template = 'emails/email_confirm.html'
    elif email_type == 'reset':
        link = f"http://localhost:8000/api/users/reset-password-confirm/{token}/"
        subject = 'Reset Your Password'
        html_template = 'emails/password_reset.html'

    html_content = render_to_string(html_template, {'link': link})

    send_mail(
        subject=subject,
        message=f'Please follow this link: {link}',  # Fallback text for email clients that don't support HTML
        html_message=html_content,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user_email],
        fail_silently=False,
    )
