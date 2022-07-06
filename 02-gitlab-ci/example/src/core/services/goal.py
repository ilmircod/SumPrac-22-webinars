from rest_framework.exceptions import ValidationError

from core.models import GoalParty, GoalPartyRequest, User, Goal
from django.utils.translation import gettext_lazy as _

max_amount_of_goals = 100
YOU_HAVE_ALREADY_SUBMITTED_A_REQUEST_TO_JOIN_THIS_GOAL = _("You have already submitted a request to join this goal")
YOU_ARE_ALREADY_ATTENDING_A_PARTY_FOR_THIS_GOAL = _("You are already attending a party for this goal")


class GoalDistributor:
    # FIXME: can_be_admin deprecated
    def __init__(self):
        self.goal_party_requests = GoalPartyRequest.objects.all()
        self.goal_party_requests_can_be_admin = self.goal_party_requests.filter(can_be_admin=True)
        self.goal_party_requests_cannot_be_admin = self.goal_party_requests.filter(can_be_admin=False)
        self.goal_party_added = 0
        self.goal_party_requests_to_delete_id = []

    def distribute(self) -> dict:
        for goal_party_request_can_be_admin in self.goal_party_requests_can_be_admin:
            goal_party = GoalParty.objects.create(
                admin=goal_party_request_can_be_admin.user, goal=goal_party_request_can_be_admin.goal
            )

            for goal_party_request_cannot_be_admin in self.goal_party_requests_cannot_be_admin:
                for _member in range(0, goal_party.goal.max_number_of_members):
                    goal_party.members.add(goal_party_request_cannot_be_admin.user)

                    self.goal_party_requests_to_delete_id.append(goal_party_request_cannot_be_admin.pk)

            self.goal_party_added += 1
            self.goal_party_requests_to_delete_id.append(goal_party_request_can_be_admin.pk)

        GoalPartyRequest.objects.filter(id__in=self.goal_party_requests_to_delete_id).delete()

        return {
            "goal_party_added": self.goal_party_added,
            "goal_party_requests_proceeded": len(self.goal_party_requests_to_delete_id),
        }


def validate_join_request(user: User, goal: Goal):
    if user.goalpartyrequest_set.filter(goal=goal):
        raise ValidationError(YOU_HAVE_ALREADY_SUBMITTED_A_REQUEST_TO_JOIN_THIS_GOAL)
    if user.goalparty_set.filter(goal=goal) or user.admin_of_goal_party.filter(goal=goal):
        raise ValidationError(YOU_ARE_ALREADY_ATTENDING_A_PARTY_FOR_THIS_GOAL)
