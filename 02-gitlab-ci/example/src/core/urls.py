from django.conf import settings
from django.http import HttpResponse
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.routers import SimpleRouter

from core.services.goal import GoalDistributor
from core.views import GoalViewSet, UserViewSet
from core.views.auth import AuthViewSet

app_name = "core"

router = SimpleRouter()
router.register("user", UserViewSet, basename="user")
router.register("goal", GoalViewSet, basename="goal")
router.register("auth", AuthViewSet, basename="auth")


def get_schema_view_description():
    return f"**🟢 Branch**: {settings.CI_COMMIT_REF_NAME}\n**🚀 Release**: {settings.CI_COMMIT_SHA}"


class CustomSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["https", "http"]
        if settings.ENVIRONMENT == "local":
            schema.schemes.reverse()
        return schema


schema_view = get_schema_view(
    openapi.Info(title=_("Sharing Service API"), default_version="v0.1", description=get_schema_view_description()),
    public=True,
    generator_class=CustomSchemaGenerator,
    permission_classes=(IsAuthenticated,),
)


def dist(request):
    return HttpResponse(GoalDistributor().distribute())


urlpatterns = [
    path("dist", dist),
    path("oauth/", include("rest_framework_social_oauth2.urls")),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui",),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

urlpatterns += router.urls
