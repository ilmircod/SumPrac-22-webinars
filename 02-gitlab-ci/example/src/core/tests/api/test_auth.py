import random

import pytest
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework import status

from core.enums import TokenEnum
from core.models import Token
from core.tests.factories.user_factory import UserFactory

incorrect_passwords = ["1234567", "123456789", "qwertyuiop", "same_as_email"]


@pytest.mark.django_db
def test_auth_sign_in_success(api_client):
    user = UserFactory.create()
    password = get_random_string()
    user.set_password(password)
    user.save()

    r = api_client.post(path="/api/auth/sign_in/", data={"email": user.email, "password": password}, format="json")

    assert r.status_code == status.HTTP_200_OK
    r_data = r.json()
    assert r_data["email"] == user.email
    assert r_data["auth_token"]

    api_client.credentials(HTTP_AUTHORIZATION="Token " + r_data["auth_token"])
    r = api_client.get(path="/api/user/")

    assert r.status_code == status.HTTP_200_OK
    assert r.json()["email"] == user.email


@pytest.mark.django_db
def test_auth_sign_in_fail(api_client):
    user = UserFactory.create()
    incorrect_password = get_random_string()
    r = api_client.post(
        path="/api/auth/sign_in/", data={"email": user.email, "password": incorrect_password}, format="json"
    )
    assert r.status_code == status.HTTP_400_BAD_REQUEST

    incorrect_email = get_random_string() + "@example.com"
    r = api_client.post(
        path="/api/auth/sign_in/", data={"email": incorrect_email, "password": incorrect_password}, format="json"
    )
    assert r.status_code == status.HTTP_400_BAD_REQUEST

    r = api_client.post(path="/api/auth/sign_in/", data={"email": user.email}, format="json")
    assert r.status_code == status.HTTP_400_BAD_REQUEST

    r = api_client.post(path="/api/auth/sign_in/", data={"password": incorrect_password}, format="json")
    assert r.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_auth_sign_up_success(api_client):
    user_sign_up_data = {
        "first_name": get_random_string(),
        "last_name": get_random_string(),
        "email": get_random_string() + "@example.com",
    }
    r = api_client.post(
        path="/api/auth/sign_up/", data={**user_sign_up_data, "password": get_random_string()}, format="json"
    )
    assert r.status_code == status.HTTP_200_OK

    r_data = r.json()

    for user_sign_up_key, user_sign_up_value in user_sign_up_data.items():
        assert r_data[user_sign_up_key] == user_sign_up_value

    api_client.credentials(HTTP_AUTHORIZATION="Token " + r_data["auth_token"])
    r = api_client.get(path="/api/user/")

    assert r.status_code == status.HTTP_200_OK
    assert r.json()["email"] == user_sign_up_data["email"]


@pytest.mark.parametrize("password", incorrect_passwords)
@pytest.mark.django_db
def test_auth_sign_up_fail(password, api_client):
    email = get_random_string() + "@example.com"
    user_sign_up_data = {
        "first_name": get_random_string(),
        "last_name": get_random_string(),
        "email": email,
        "password": email if password == "same_as_email" else password,
    }

    r = api_client.post(path="/api/auth/sign_up/", data=user_sign_up_data, format="json")
    assert r.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_auth_confirm_email_success(api_client):
    user = UserFactory.create()

    assert user.is_email_verified is False

    token = Token.objects.create(user=user, token_type=TokenEnum.EMAIL_VERIFICATION)
    api_client.force_authenticate(user=user)
    r = api_client.post(path="/api/auth/confirm_email/", data={"token": token.value})

    user.refresh_from_db()

    assert r.status_code == status.HTTP_200_OK
    assert user.is_email_verified is True
    assert not Token.objects.filter(pk=token.pk)


@pytest.mark.django_db
def test_auth_confirm_email_fail(api_client):
    user = UserFactory.create()

    api_client.force_authenticate(user=user)
    r = api_client.post(path="/api/auth/confirm_email/", data={"token": get_random_string()})

    user.refresh_from_db()

    assert r.status_code == status.HTTP_400_BAD_REQUEST

    token = Token.objects.create(user=user, token_type=TokenEnum.FORGOT_PASSWORD)
    r = api_client.post(path="/api/auth/confirm_email/", data={"token": token.value})

    user.refresh_from_db()

    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert user.is_email_verified is False


@pytest.mark.django_db
def test_auth_send_email_confirmation_success(api_client):
    assert Token.objects.count() == 0

    user = UserFactory.create()
    api_client.force_authenticate(user=user)
    r = api_client.post(path="/api/auth/send_email_confirmation/")

    assert r.status_code == status.HTTP_200_OK
    assert r.json()["id"] == user.pk
    assert Token.objects.get(user=user, expiration_date__gt=timezone.now(), token_type=TokenEnum.EMAIL_VERIFICATION)


@pytest.mark.django_db
def test_auth_send_email_confirmation_fail(api_client):
    r = api_client.post(path="/api/auth/send_email_confirmation/")

    assert r.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_auth_forgot_password_success(api_client):
    assert Token.objects.count() == 0

    user = UserFactory.create()
    r = api_client.post(path="/api/auth/forgot_password/", data={"email": user.email})

    assert r.status_code == status.HTTP_200_OK
    assert r.json()["email"] == user.email
    assert Token.objects.get(user=user, expiration_date__gt=timezone.now(), token_type=TokenEnum.FORGOT_PASSWORD)


@pytest.mark.django_db
def test_auth_forgot_password_fail(api_client):
    r = api_client.post(path="/api/auth/forgot_password/", data={"email": get_random_string() + "@example.com"})

    assert r.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_auth_set_new_password_success(api_client):
    user = UserFactory.create()
    token = Token.objects.create(user=user, token_type=TokenEnum.FORGOT_PASSWORD)

    incorrect_password = random.choice(incorrect_passwords[0:2])
    assert not user.check_password(incorrect_password)
    r = api_client.post(path="/api/auth/set_new_password/", data={"token": token.value, "password": incorrect_password})
    assert r.status_code == status.HTTP_400_BAD_REQUEST

    password = get_random_string()
    assert not user.check_password(password)
    r = api_client.post(path="/api/auth/set_new_password/", data={"token": token.value, "password": password})
    assert r.status_code == status.HTTP_200_OK

    user.refresh_from_db()
    assert user.check_password(password)
    assert not Token.objects.filter(pk=token.pk)


@pytest.mark.parametrize("password", incorrect_passwords)
@pytest.mark.django_db
def test_auth_set_new_password_fail_incorrect_password(password, api_client):
    user = UserFactory.create()
    token = Token.objects.create(user=user, token_type=TokenEnum.FORGOT_PASSWORD)

    r = api_client.post(
        path="/api/auth/set_new_password/",
        data={"token": token.value, "password": user.email if password == "same_as_email" else password},
    )

    assert r.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_auth_set_new_password_fail_incorrect_token(api_client):
    r = api_client.post(
        path="/api/auth/set_new_password/", data={"token": get_random_string(), "password": get_random_string()}
    )

    assert r.status_code == status.HTTP_400_BAD_REQUEST
