from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.models import Goal, GoalPartyRequest
from core.models.goal import GoalCategory
from core.serializers.goal import (
    GoalPartyRequestSerializer,
    GoalSerializer,
    GoalCategorySerializer,
)
from core.services.goal import validate_join_request


class GoalViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    serializer_class = GoalSerializer
    queryset = Goal.objects.all()
    permission_classes_by_action = {"join": [IsAuthenticated]}
    permission_classes = (AllowAny,)

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        q_clause = Q()
        category_id = self.request.query_params.get("category_id")

        if category_id:
            q_clause &= Q(category__id=category_id)

        return queryset.filter(q_clause)

    @swagger_auto_schema(request_body=no_body, responses={200: GoalPartyRequestSerializer()})
    @action(methods=["POST"], detail=True)
    def join(self, *args, **kwargs):
        user = self.request.user
        goal = get_object_or_404(Goal, pk=kwargs.get("pk"))

        validate_join_request(user=user, goal=goal)

        goal_party_request = GoalPartyRequest.objects.create(user=user, goal=goal,)
        return Response(GoalPartyRequestSerializer(goal_party_request, context={"request": self.request}).data)

    @swagger_auto_schema(responses={200: GoalCategorySerializer()})
    @action(methods=["GET"], detail=False)
    def categories(self, *args, **kwargs):
        return Response(
            GoalCategorySerializer(GoalCategory.objects.all(), many=True, context={"request": self.request}).data
        )

    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter(name="category_id", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,)]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
