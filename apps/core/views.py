from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET

from apps.bookings.forms import BookingForm
from apps.procedures.models import FAQ, Category, Procedure, ResultCase

from .models import SiteSettings, Testimonial
from .seo import clinic_schema, faq_schema, to_jsonld


def home(request):
    site = SiteSettings.load()
    cases = list(ResultCase.objects.published().select_related("procedure__category"))
    hero_case = next((c for c in cases if c.is_hero), cases[0] if cases else None)
    categories = Category.objects.prefetch_related(
        Prefetch("procedures", queryset=Procedure.objects.published().filter(is_featured=True), to_attr="featured")
    )
    faqs = FAQ.objects.filter(procedure__isnull=True, is_published=True)
    context = {
        "hero_case": hero_case,
        "cases": cases,
        "case_categories": sorted({c.procedure.category for c in cases}, key=lambda cat: cat.order),
        "categories": [c for c in categories if c.featured],
        "testimonials": Testimonial.objects.filter(is_published=True).select_related("procedure")[:6],
        "faqs": faqs,
        "form": BookingForm(),
        "page_context": {"type": "home", "title": _("Home page")},
        "jsonld": to_jsonld(*(s for s in [clinic_schema(site, request), faq_schema(faqs)] if s)),
    }
    return render(request, "core/home.html", context)


@require_GET
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /panel/",
        "Disallow: /admin/",
        "Disallow: /*/book/submit/",
        f"Sitemap: {request.build_absolute_uri(reverse('sitemap'))}",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


def page_not_found(request, exception):
    return render(request, "core/404.html", {"page_context": {"type": "404", "title": "404"}}, status=404)
