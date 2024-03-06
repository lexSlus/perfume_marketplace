from celery import shared_task
from accounts.utils import send_confirmation_email


@shared_task
def send_confirmation_email_task(user_email, confirmation_token, password=None):
    send_confirmation_email(user_email, confirmation_token, password)
