from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from rest_framework.request import Request

from core.enums import TokenEnum
from core.models import Token, User
from core.tasks import send_email


def send_email_confirmation(request: Request):
    def _generate_confirmation_link(_request: Request):
        token = Token.objects.create(user=request.user, token_type=TokenEnum.EMAIL_VERIFICATION)
        return f"{_request.META.get('HTTP_ORIGIN')}/auth/confirm_email/{token.value}/"

    h1 = _("Almost done!")
    text = _("To complete registration and confirm your email address, click on the button below")
    button_text = _("Confirm")
    button_link = _generate_confirmation_link(request)
    subject = _("Almost done!")

    html_message = render_to_string(
        "email/base.html", context={"h1": h1, "text": text, "button_text": button_text, "button_link": button_link},
    )
    send_email.delay(subject=subject, html_message=html_message, recipient_list=[request.user.email])


def send_email_forgot_password(request: Request, user: User):
    def generate_forgot_password_link(_request: Request, _user: User):
        token = Token.objects.create(user=_user, token_type=TokenEnum.FORGOT_PASSWORD)
        return f"{_request.META.get('HTTP_ORIGIN')}/auth/forgot_password/{token.value}/"

    h1 = _("Password recovery")
    text = _("To set a new password, follow the link below")
    button_text = _("Set new password")
    button_link = generate_forgot_password_link(request, user)
    subject = _("Password recovery")

    html_message = render_to_string(
        "email/base.html", context={"h1": h1, "text": text, "button_text": button_text, "button_link": button_link},
    )
    send_email.delay(subject=subject, html_message=html_message, recipient_list=[user.email])
