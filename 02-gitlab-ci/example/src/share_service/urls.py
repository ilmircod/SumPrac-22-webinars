from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _

urlpatterns = [
    path("jet/", include("jet.urls", "jet")),
    path("admin/", admin.site.urls),
    path("api/", include("core.urls", namespace="api")),
]

urlpatterns += static(settings.STATIC_URL)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = _("Share Service Admin")
admin.site.site_title = _("Share Service Admin")
admin.site.index_title = _("Welcome to Share Service Admin")

if "rosetta" in settings.INSTALLED_APPS:
    urlpatterns += [path("rosetta/", include("rosetta.urls"))]

if settings.ENABLE_SENTRY:

    def trigger_error(request):
        return 1 / 0

    urlpatterns += [path("sentry-debug/", trigger_error)]
