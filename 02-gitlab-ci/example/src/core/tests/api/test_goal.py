import random

import pytest
from rest_framework import status

from core.models.goal import GoalCategory, GoalPartyRequest, GoalParty
from core.services.goal import (
    YOU_HAVE_ALREADY_SUBMITTED_A_REQUEST_TO_JOIN_THIS_GOAL,
    YOU_ARE_ALREADY_ATTENDING_A_PARTY_FOR_THIS_GOAL,
)
from core.tests.factories.goal_factory import GoalFactory, GoalCategoryFactory
from core.tests.factories.user_factory import UserFactory


@pytest.mark.django_db
def test_get_goal_list(api_client):
    goals_count = random.randint(1, 10)
    [GoalFactory.create() for _ in range(0, goals_count)]

    r = api_client.get(path="/api/goal/")

    assert r.status_code == status.HTTP_200_OK
    assert len(r.json()) == goals_count

    goal_category_pk = random.choice(GoalCategory.objects.all()).pk

    r = api_client.get(path=f"/api/goal/?category_id={goal_category_pk}")
    for goal in r.json():
        assert goal["category"]["id"] == goal_category_pk


@pytest.mark.django_db
def test_get_goal_category_list(api_client):
    goals_category_count = random.randint(1, 10)
    [GoalCategoryFactory.create() for _ in range(0, goals_category_count)]

    r = api_client.get(path="/api/goal/categories/")

    assert r.status_code == status.HTTP_200_OK
    assert len(r.json()) == goals_category_count
    assert r.json()[0]["id"] and r.json()[0]["title"] and r.json()[0]["image"]


@pytest.mark.django_db
def test_get_goal_not_authenticated_user(api_client):
    goal = GoalFactory.create()

    r = api_client.get(path=f"/api/goal/{goal.pk}/")

    assert r.status_code == status.HTTP_200_OK
    assert r.json()["id"] == goal.pk
    assert not r.json()["my_goal_party"]


@pytest.mark.django_db
def test_get_another_goal_authenticated_user(api_client):
    user = UserFactory.create()
    goal_party = GoalParty.objects.create(goal=GoalFactory.create(), admin=UserFactory.create())
    goal_party.members.add(user)

    api_client.force_authenticate(user=user)
    r = api_client.get(path=f"/api/goal/{GoalFactory.create().pk}/")

    assert r.status_code == status.HTTP_200_OK
    assert not r.json()["my_goal_party"]


@pytest.mark.django_db
def test_get_goal_authenticated_admin_user(api_client):
    goal = GoalFactory.create()
    user = UserFactory.create()
    goal_party = GoalParty.objects.create(goal=goal, admin=user)

    api_client.force_authenticate(user=user)
    r = api_client.get(path=f"/api/goal/{goal.pk}/")

    assert r.status_code == status.HTTP_200_OK
    r_data = r.json()
    assert r_data["my_goal_party"]["id"] == goal_party.pk
    assert r_data["id"] == goal.pk


@pytest.mark.django_db
def test_get_goal_authenticated_member_user(api_client):
    user = UserFactory.create()
    goal = GoalFactory.create()
    goal_party = GoalParty.objects.create(goal=goal, admin=UserFactory.create())
    goal_party.members.add(user)

    api_client.force_authenticate(user=user)
    r = api_client.get(path=f"/api/goal/{goal.pk}/")

    assert r.status_code == status.HTTP_200_OK
    r_data = r.json()
    assert r_data["my_goal_party"]["id"] == goal_party.pk
    assert r_data["id"] == goal.pk


@pytest.mark.django_db
def test_join_goal_success(api_client):
    goal = GoalFactory.create()
    user = UserFactory.create()

    api_client.force_authenticate(user=user)
    r = api_client.post(path=f"/api/goal/{goal.pk}/join/")

    assert r.status_code == status.HTTP_200_OK
    assert r.json()["goal"]["id"] == goal.pk
    assert r.json()["user"]["id"] == user.pk
    assert GoalPartyRequest.objects.get(goal=goal, user=user)


@pytest.mark.django_db
def test_join_goal_fail(api_client):
    # if the user is not authenticated
    goal = GoalFactory.create()
    r = api_client.post(path=f"/api/goal/{goal.pk}/join/")

    assert r.status_code == status.HTTP_401_UNAUTHORIZED

    # if the user has already sent a request for joining this goal
    user = UserFactory.create()
    GoalPartyRequest.objects.create(goal=goal, user=user)
    api_client.force_authenticate(user=user)
    r = api_client.post(path=f"/api/goal/{goal.pk}/join/")

    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert r.json()[0] == YOU_HAVE_ALREADY_SUBMITTED_A_REQUEST_TO_JOIN_THIS_GOAL

    # if the user is a member of the goal
    goal = GoalFactory.create()
    goal_party = GoalParty.objects.create(goal=goal, admin=UserFactory.create())
    goal_party.members.add(user)
    r = api_client.post(path=f"/api/goal/{goal.pk}/join/")

    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert r.json()[0] == YOU_ARE_ALREADY_ATTENDING_A_PARTY_FOR_THIS_GOAL

    # if the user is a goal admin
    goal = GoalFactory.create()
    GoalParty.objects.create(goal=goal, admin=user)
    r = api_client.post(path=f"/api/goal/{goal.pk}/join/")

    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert r.json()[0] == YOU_ARE_ALREADY_ATTENDING_A_PARTY_FOR_THIS_GOAL
