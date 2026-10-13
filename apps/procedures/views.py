from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import gettext as _

from apps.bookings.forms import BookingForm
from apps.core.seo import breadcrumb_schema, faq_schema, procedure_schema, to_jsonld

from .models import Category, Procedure, ResultCase


def procedure_list(request):
    categories = Category.objects.prefetch_related(
        Prefetch("procedures", queryset=Procedure.objects.published(), to_attr="live")
    )
    return render(request, "procedures/list.html", {
        "categories": [c for c in categories if c.live],
        "page_context": {"type": "procedures", "title": _("All treatments")},
    })


def procedure_detail(request, slug):
    procedure = get_object_or_404(
        Procedure.objects.published().select_related("category").prefetch_related("sections"),
        slug=slug,
    )
    faqs = procedure.faqs.filter(is_published=True)
    cases = procedure.cases.filter(is_published=True)
    related = Procedure.objects.published().filter(category=procedure.category).exclude(pk=procedure.pk)[:3]
    if not related:
        related = Procedure.objects.published().exclude(pk=procedure.pk)[:3]
    form = BookingForm(initial={"procedure": procedure})
    crumbs = [(_("Home"), reverse("core:home")), (_("Treatments"), reverse("procedures:list")),
              (procedure.tr("title"), procedure.get_absolute_url())]
    schemas = [procedure_schema(procedure, request), breadcrumb_schema(crumbs, request), faq_schema(faqs)]
    return render(request, "procedures/detail.html", {
        "procedure": procedure,
        "sections": list(procedure.sections.all()),
        "faqs": faqs,
        "cases": cases,
        "related": related,
        "form": form,
        "page_context": {
            "type": "procedure",
            "title": procedure.tr("title"),
            "procedure": procedure.tr("title", "fa"),
            "category": procedure.category.tr("name", "fa"),
        },
        "jsonld": to_jsonld(*(s for s in schemas if s)),
    })


def results(request):
    cases = ResultCase.objects.published().select_related("procedure__category")
    categories = sorted({c.procedure.category for c in cases}, key=lambda cat: cat.order)
    return render(request, "procedures/results.html", {
        "cases": cases,
        "case_categories": categories,
        "page_context": {"type": "results", "title": _("Before and after gallery")},
    })
