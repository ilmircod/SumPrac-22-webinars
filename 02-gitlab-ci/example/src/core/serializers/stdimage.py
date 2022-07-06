from rest_framework import serializers

from core.models.goal import Goal
from core.models.user import User


class StdImageSerializer(serializers.Serializer):
    original = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    cls_map = {User: "avatar", Goal: "image"}

    def build_url(self, field):
        """
        This method builds file urls - current work for User, Goal.
        """
        if not field:
            return

        request = self.context["request"]
        host = request.get_host()
        abs_url = f"{host}{field.url}"

        if "://" not in host:
            abs_url = f"{request.scheme}://{abs_url}"

        return abs_url

    def get_original(self, obj):
        if not self.cls_map.get(obj.__class__):
            return
        field = getattr(obj, self.cls_map[obj.__class__])
        return self.build_url(field)

    def get_thumbnail(self, obj):
        if not self.cls_map.get(obj.__class__):
            return
        field = getattr(obj, self.cls_map[obj.__class__])
        return self.build_url(field.thumbnail if field else field)

    def update(self, instance, validated_data):
        return NotImplementedError

    def create(self, validated_data):
        return NotImplementedError
