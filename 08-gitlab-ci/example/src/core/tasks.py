from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task()
def send_email(subject, html_message, recipient_list):
    if isinstance(recipient_list, str):
        recipient_list = [recipient_list]

    send_mail(
        subject=subject,
        message=None,
        html_message=html_message,
        from_email=settings.EMAIL_HOST_SENDER,
        recipient_list=recipient_list,
    )
