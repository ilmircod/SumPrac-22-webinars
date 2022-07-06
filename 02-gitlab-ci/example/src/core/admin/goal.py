from django.contrib import admin

from core.models import GoalParty, GoalPartyRequest
from core.models.goal import GoalCategory


class GoalPartyAdmin(admin.ModelAdmin):
    model = GoalParty


class GoalPartyInline(admin.TabularInline):
    model = GoalParty
    extra = 0


class GoalAdmin(admin.ModelAdmin):
    inlines = [GoalPartyInline]
    list_display = ("title", "image_preview")


class GoalPartyRequestAdmin(admin.ModelAdmin):
    model = GoalPartyRequest


class GoalCategoryAdmin(admin.ModelAdmin):
    model = GoalCategory
