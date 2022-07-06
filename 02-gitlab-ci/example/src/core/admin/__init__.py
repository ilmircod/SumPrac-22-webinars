from django.contrib import admin

from core.admin.goal import GoalAdmin, GoalPartyAdmin, GoalPartyRequestAdmin, GoalCategoryAdmin
from core.admin.user import TokenAdmin, UserAdmin
from core.models import Goal, GoalParty, GoalPartyRequest, Token, User
from core.models.goal import GoalCategory

admin.site.register(User, UserAdmin)
admin.site.register(Goal, GoalAdmin)
admin.site.register(GoalParty, GoalPartyAdmin)
admin.site.register(GoalPartyRequest, GoalPartyRequestAdmin)
admin.site.register(Token, TokenAdmin)
admin.site.register(GoalCategory, GoalCategoryAdmin)
