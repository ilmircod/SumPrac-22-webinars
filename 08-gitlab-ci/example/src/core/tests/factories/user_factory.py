import factory
from factory.django import DjangoModelFactory

from core.models import User


class UserFactory(DjangoModelFactory):
    """Factory to create User objects"""

    email = factory.LazyAttribute(lambda a: f"{a.first_name}.{a.last_name}@example.com".lower())
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    class Meta:
        model = User
