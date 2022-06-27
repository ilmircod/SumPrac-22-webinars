from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from stdimage import StdImageField

from core.models.base import BaseModel
from core.services.helpers import build_absolute_image_uri


class GoalCategory(BaseModel):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="goal_categories")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "goal categories"


class Goal(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = StdImageField(upload_to="goal_images", variations={"thumbnail": {"width": 100, "height": 75}})
    max_number_of_members = models.PositiveSmallIntegerField()
    category = models.ForeignKey("GoalCategory", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.title

    def image_preview(self):
        return format_html(
            '<img src={} alt={} style="padding: 1px; display: inline-block;'
            'height: 20px; border-radius: 50%; width: 1;"></img>',
            build_absolute_image_uri(self.image),
            self.title,
        )

    image_preview.short_description = _("image")


class GoalParty(BaseModel):
    goal = models.ForeignKey("Goal", on_delete=models.CASCADE)
    admin = models.ForeignKey("User", on_delete=models.CASCADE, related_name="admin_of_goal_party")
    members = models.ManyToManyField("User", blank=True)

    def __str__(self):
        return f"{_('Party for goal')} {self.goal}"

    class Meta:
        verbose_name_plural = _("goal parties")


class GoalPartyRequest(BaseModel):
    goal = models.ForeignKey("Goal", on_delete=models.CASCADE)
    user = models.ForeignKey("User", on_delete=models.CASCADE)

    def __str__(self):
        return f"{_('Request to party')} {self.goal} {_('from')} {self.user}"
