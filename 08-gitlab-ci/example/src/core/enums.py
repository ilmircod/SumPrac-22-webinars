from django.db.models import Choices
from django.utils.translation import gettext_lazy as _


class TokenEnum(Choices):
    EMAIL_VERIFICATION = _("EMAIL VERIFICATION")
    FORGOT_PASSWORD = _("FORGOT PASSWORD")
