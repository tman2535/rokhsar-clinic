import datetime as dt

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_POST

from apps.core.i18n import current_lang
from apps.core.jalali import format_date, localize_digits
from apps.core.utils import client_ip, rate_limited
from apps.notifications.services import notify_booking

from .forms import BookingForm, date_is_bookable, slot_states
from .models import Appointment


def _wants_json(request) -> bool:
    return request.headers.get("x-requested-with") == "fetch" or "application/json" in request.headers.get("accept", "")


@require_POST
def book(request):
    ip = client_ip(request)
    if rate_limited(f"book:{ip}", limit=6, window=600):
        msg = _("Too many requests. Please try again in a few minutes or call the clinic.")
        return JsonResponse({"ok": False, "errors": {"__all__": [msg]}}, status=429)

    form = BookingForm(request.POST)
    if not form.is_valid():
        if _wants_json(request):
            errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
            return JsonResponse({"ok": False, "errors": errors}, status=400)
        return render(request, "bookings/form_page.html", {"form": form}, status=400)

    with transaction.atomic():
        appointment = form.save(commit=False)
        appointment.language = current_lang()
        appointment.ip_address = ip
        appointment.save()
        notify_booking(appointment)

    lang = current_lang()
    if _wants_json(request):
        return JsonResponse({
            "ok": True,
            "code": appointment.code,
            "date": format_date(appointment.preferred_date, lang),
            "time": localize_digits(appointment.time_slot, lang),
            "procedure": appointment.procedure.tr("title") if appointment.procedure else "",
        })
    request.session["last_booking"] = appointment.code
    return redirect("bookings:done", code=appointment.code)


def done(request, code):
    # Only the visitor who just booked can see the confirmation page.
    if request.session.get("last_booking") != code:
        return redirect("core:home")
    appointment = get_object_or_404(Appointment, code=code)
    return render(request, "bookings/done.html", {"appointment": appointment})


def form_page(request):
    """No-JavaScript fallback page with the same booking form."""
    return render(request, "bookings/form_page.html", {"form": BookingForm()})


@require_GET
def slots(request):
    try:
        date = dt.date.fromisoformat(request.GET.get("date", ""))
    except ValueError:
        return JsonResponse({"ok": False, "slots": []}, status=400)
    if not date_is_bookable(date):
        return JsonResponse({"ok": True, "closed": True, "slots": []})
    lang = current_lang()
    data = [{**s, "label": localize_digits(s["time"], lang)} for s in slot_states(date)]
    return JsonResponse({"ok": True, "closed": False, "slots": data, "label": format_date(date, lang)})
