from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.core.views import robots_txt
from apps.procedures.sitemaps import ProcedureSitemap, StaticSitemap

sitemaps = {"static": StaticSitemap, "procedures": ProcedureSitemap}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("panel/", include("apps.panel.urls")),
    path("", include("apps.notifications.urls")),
    path("robots.txt", robots_txt, name="robots"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    path("", include("apps.core.urls")),
    path("treatments/", include("apps.procedures.urls")),
    path("book/", include("apps.bookings.urls")),
    path("chat/", include("apps.chat.urls")),
    prefix_default_language=True,
)

# Uploaded media: served by Django in development, or when SERVE_MEDIA=1 on a
# small single-server install. Behind nginx, let nginx serve /media/ instead.
if settings.DEBUG or settings.SERVE_MEDIA:
    from django.urls import re_path
    from django.views.static import serve

    urlpatterns += [re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT})]

handler404 = "apps.core.views.page_not_found"

admin.site.site_header = "Rokhsar — مدیریت محتوا"
admin.site.site_title = "Rokhsar"
