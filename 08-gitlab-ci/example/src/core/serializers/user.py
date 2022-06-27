from rest_framework import serializers
from rest_framework.authtoken.models import Token

from core.models import User
from core.serializers.stdimage import StdImageSerializer


class UserSerializer(serializers.ModelSerializer):
    # FIXME: show avatar field as StdImageSerializer
    avatar = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "is_email_verified",
            "avatar",
        )
        extra_kwargs = {"is_email_verified": {"read_only": True}, "email": {"read_only": True}}

    def get_avatar(self, obj):
        return StdImageSerializer(obj, context={"request": self.context.get("request")}).data


class UserAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("avatar",)


class UserAuthOutputSerializer(UserSerializer):
    auth_token = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("auth_token",)

    def get_auth_token(self, obj):
        token, created = Token.objects.get_or_create(user=obj)
        return token.key


class UserAuthSignInSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "password")


class UserAuthSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password")


class ConfirmEmailSerializer(serializers.Serializer):
    token = serializers.CharField()

    def update(self, instance, validated_data):
        raise NotImplementedError

    def create(self, validated_data):
        raise NotImplementedError


class SetNewPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField()

    def update(self, instance, validated_data):
        raise NotImplementedError

    def create(self, validated_data):
        raise NotImplementedError


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.CharField()

    def update(self, instance, validated_data):
        raise NotImplementedError

    def create(self, validated_data):
        raise NotImplementedError
