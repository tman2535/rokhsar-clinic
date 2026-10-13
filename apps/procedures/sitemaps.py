from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Procedure


class StaticSitemap(Sitemap):
    i18n = True
    alternates = True
    x_default = True
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ["core:home", "procedures:list", "procedures:results"]

    def location(self, item):
        return reverse(item)


class ProcedureSitemap(Sitemap):
    i18n = True
    alternates = True
    x_default = True
    priority = 0.9
    changefreq = "monthly"

    def items(self):
        return Procedure.objects.published()

    def lastmod(self, obj):
        return obj.updated_at
