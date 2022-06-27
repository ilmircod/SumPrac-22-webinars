import pytest
from rest_framework import status

from core.serializers.user import UserSerializer
from core.tests.factories.user_factory import UserFactory
from core.tests.helpers import create_temp_image, get_writeable_serializer_fields


@pytest.mark.django_db
def test_get_current_user_success(api_client):
    user = UserFactory.create()
    api_client.force_authenticate(user=user)

    r = api_client.get(path="/api/user/")

    assert r.status_code == status.HTTP_200_OK
    assert r.json()["email"] == user.email


@pytest.mark.django_db
def test_get_current_user_fail(api_client):
    r = api_client.get(path="/api/user/")

    assert r.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_user_success(api_client):
    user_1 = UserFactory.create()
    user_2 = UserFactory.create()
    api_client.force_authenticate(user=user_1)

    r = api_client.get(path=f"/api/user/{user_2.pk}/")

    assert r.status_code == status.HTTP_200_OK
    assert r.json()["email"] == user_2.email


@pytest.mark.django_db
def test_get_user_fail(api_client):
    user = UserFactory.create()
    r = api_client.get(path=f"/api/user/{user.pk}/")

    assert r.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_upload_user_avatar_success(api_client):
    user = UserFactory.create()
    api_client.force_authenticate(user=user)

    avatar_suffix = ".jpg"
    avatar_file = create_temp_image(avatar_suffix)

    r = api_client.post(path="/api/user/avatar/", data={"avatar": avatar_file}, format="multipart")

    assert r.status_code == status.HTTP_200_OK

    r_data = r.json()
    avatar_file_name = avatar_file.name.replace("/tmp/", "")
    avatar_file_name_thumbnail = avatar_file_name.replace(avatar_suffix, f".thumbnail{avatar_suffix}")

    assert avatar_file_name.split("/")[-1] in r_data["avatar"]["original"]
    assert avatar_file_name_thumbnail.split("/")[-1] in r_data["avatar"]["thumbnail"]


@pytest.mark.django_db
def test_upload_user_avatar_fail(api_client):
    avatar_suffix = ".jpg"
    avatar_file = create_temp_image(avatar_suffix)

    r = api_client.post(path="/api/user/avatar/", data={"avatar": avatar_file}, format="multipart")

    assert r.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_patch_user_avatar_success(api_client):
    user = UserFactory.create()
    temp_user = UserFactory.create()
    temp_user_dict = temp_user.__dict__
    user_dict_to_update = dict()

    writeable_serializer_fields = get_writeable_serializer_fields(UserSerializer)

    for field in writeable_serializer_fields:
        user_dict_to_update[field] = temp_user_dict[field]

    api_client.force_authenticate(user=user)
    r = api_client.patch(path=f"/api/user/{user.pk}/", data=user_dict_to_update, format="json")

    assert r.status_code == status.HTTP_200_OK
    r_data = r.json()

    for field in writeable_serializer_fields:
        assert r_data[field] == temp_user_dict[field]


@pytest.mark.django_db
def test_patch_user_avatar_fail(api_client):
    user = UserFactory.create()
    temp_user = UserFactory.create()
    temp_user_dict = temp_user.__dict__
    user_dict_to_update = dict()

    writeable_serializer_fields = get_writeable_serializer_fields(UserSerializer)

    for field in writeable_serializer_fields:
        user_dict_to_update[field] = temp_user_dict[field]

    r = api_client.patch(path=f"/api/user/{user.pk}/", data=user_dict_to_update, format="json")
    assert r.status_code == status.HTTP_401_UNAUTHORIZED

    api_client.force_authenticate(user=user)
    r = api_client.patch(path=f"/api/user/{temp_user.pk}/", data=user_dict_to_update, format="json")
    assert r.status_code == status.HTTP_403_FORBIDDEN
