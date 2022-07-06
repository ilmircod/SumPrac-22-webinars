from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.models import User
from core.serializers.user import UserAvatarSerializer, UserSerializer


class UserViewSet(GenericViewSet, RetrieveModelMixin):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_parsers(self):
        try:
            _action = self.action
        except AttributeError:
            return super().get_parsers()

        if _action in ("avatar",):
            return [MultiPartParser]

        return super().get_parsers()

    @swagger_auto_schema(
        operation_summary="Get current user", operation_id="user_read_current", responses={200: UserSerializer()}
    )
    def list(self, request, *args, **kwargs):
        return Response(self.serializer_class(self.request.user, context={"request": request}).data)

    @swagger_auto_schema(
        operation_summary="Upload a user avatar", request_body=UserAvatarSerializer, responses={200: UserSerializer()}
    )
    @action(methods=["POST"], detail=False)
    def avatar(self, request, *args, **kwargs):
        avatar_file = request.data.get("avatar")
        user = self.request.user
        user.avatar.save(name=avatar_file.name, content=avatar_file)
        return Response(self.serializer_class(user, context={"request": request}).data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance != self.request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
