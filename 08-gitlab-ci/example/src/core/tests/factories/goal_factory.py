import random
from decimal import Decimal

import factory
from factory.django import DjangoModelFactory

from core.models import Goal
from core.models.goal import GoalCategory


class GoalCategoryFactory(DjangoModelFactory):
    title = factory.Faker("word")
    image = factory.django.ImageField()

    class Meta:
        model = GoalCategory


class GoalFactory(DjangoModelFactory):
    """Factory to create Goal objects"""

    title = factory.Faker("word")
    description = factory.Faker("word")
    image = factory.django.ImageField()
    max_number_of_members = Decimal(random.randrange(0, 10))
    category = factory.SubFactory(GoalCategoryFactory)

    class Meta:
        model = Goal
