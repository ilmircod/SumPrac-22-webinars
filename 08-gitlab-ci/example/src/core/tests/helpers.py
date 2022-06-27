import tempfile
from typing import Type

from PIL import Image
from rest_framework import serializers


def create_temp_image(avatar_suffix: str):
    image = Image.new("RGB", (100, 100))

    avatar_file = tempfile.NamedTemporaryFile(suffix=avatar_suffix)
    image.save(avatar_file)
    avatar_file.seek(0)
    return avatar_file


def get_writeable_serializer_fields(serializer: Type[serializers.ModelSerializer]) -> list:
    writeable_fields = []

    for key, field in serializer().get_fields().items():
        if not field.read_only:
            writeable_fields.append(key)

    return writeable_fields
