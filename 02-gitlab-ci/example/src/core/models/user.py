import datetime
import uuid

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from stdimage import StdImageField

from core.enums import TokenEnum
from share_service.settings import VERIFICATION_TOKEN_EXPIRATION_TIME


class CustomUserManager(UserManager):
    def create_superuser(self, email, password=None, **extra_fields):
        super().create_superuser(username=email, email=email, password=password)


class User(AbstractUser):
    email = models.EmailField(_("email address"), blank=True, unique=True)
    avatar = StdImageField(
        upload_to="avatars", blank=True, null=True, variations={"thumbnail": {"width": 100, "height": 75}}
    )
    is_email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.username = self.email
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.email


class Token(models.Model):
    value = models.CharField(max_length=200)
    token_type = models.CharField(max_length=55, choices=TokenEnum.choices)
    expiration_date = models.DateTimeField()
    user = models.ForeignKey("User", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.value = uuid.uuid4()
        self.expiration_date = timezone.now() + datetime.timedelta(seconds=VERIFICATION_TOKEN_EXPIRATION_TIME)
        super(Token, self).save(*args, **kwargs)
