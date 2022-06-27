from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.forms import UserChangeForm as DefaultUserChangeForm

from core.models import User


class UserChangeForm(DefaultUserChangeForm):
    class Meta(DefaultUserChangeForm.Meta):
        model = User


class UserAdmin(DefaultUserAdmin):
    form = UserChangeForm

    fieldsets = DefaultUserAdmin.fieldsets + (("Additional info", {"fields": ("avatar",)},),)


class TokenAdmin(admin.ModelAdmin):
    pass
