from django.contrib.auth import password_validation
from django.contrib.auth.password_validation import UserAttributeSimilarityValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _

from core.models import User


def validate_sign_up_data(sign_up_data: dict) -> list:
    """Validates user's sign up data and returns list of error messages."""
    error_messages = []

    if User.objects.filter(email=sign_up_data.get("email")).exists():
        error_messages.append(_("Email has already been taken"))

    error_messages.extend(validate_password(sign_up_data))

    return error_messages


def validate_password(user_data: dict) -> list:
    error_messages = []

    try:
        password = user_data.get("password")
        password_validation.validate_password(password=password)

        # We create a temporary user, which we do not write to the database,
        # in order to check the password with the UserAttributeSimilarityValidator
        UserAttributeSimilarityValidator().validate(password, User(email=user_data.get("email")))
    except DjangoValidationError as e:
        for password_error in e.error_list:
            error_messages.extend(password_error.messages)

    return error_messages
