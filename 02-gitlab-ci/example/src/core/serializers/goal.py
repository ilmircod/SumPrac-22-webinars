from django.db.models import Q
from rest_framework import serializers
from sentry_sdk import capture_exception

from core.models import Goal, GoalPartyRequest
from core.models.goal import GoalCategory, GoalParty
from core.serializers.user import UserSerializer


class GoalCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalCategory
        fields = ("id", "title", "image")


class GoalCompactSerializer(serializers.ModelSerializer):
    category = GoalCategorySerializer()

    class Meta:
        model = Goal
        fields = (
            "id",
            "title",
            "description",
            "image",
            "category",
        )


class GoalPartyRequestSerializer(serializers.ModelSerializer):
    goal = GoalCompactSerializer()
    user = UserSerializer()

    class Meta:
        model = GoalPartyRequest
        fields = (
            "goal",
            "user",
        )


class GoalPartyCompactSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalParty
        fields = ("id",)


class GoalPartySerializer(GoalPartyCompactSerializer):
    goal = GoalCompactSerializer()
    admin = UserSerializer()
    members = UserSerializer(many=True)

    class Meta(GoalPartyCompactSerializer.Meta):
        fields = (
            *GoalPartyCompactSerializer.Meta.fields,
            "goal",
            "admin",
            "members",
        )


class GoalSerializer(GoalCompactSerializer):
    my_goal_party = serializers.SerializerMethodField()

    class Meta(GoalCompactSerializer.Meta):
        fields = (
            *GoalCompactSerializer.Meta.fields,
            "my_goal_party",
        )

    def get_my_goal_party(self, obj):
        user = self.context["request"].user
        if user.pk:
            try:
                goal_party = GoalParty.objects.get(Q(admin=user) | Q(members__in=[user]), goal=obj)
            except (GoalParty.DoesNotExist, GoalParty.MultipleObjectsReturned) as e:
                capture_exception(e)
                return

            return GoalPartyCompactSerializer(goal_party).data
