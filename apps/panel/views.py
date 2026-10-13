"""Staff panel for the doctor and the secretary."""
import csv
import datetime as dt
from functools import wraps

from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, F, Q
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.bookings.models import Appointment
from apps.chat.models import Message, Thread
from apps.core.jalali import format_date
from apps.core.models import SiteSettings
from apps.notifications.backends import Notice, bot_call
from apps.notifications.models import Channel, Event
from apps.notifications.services import absolute, deliver, notify_booking
from apps.procedures.models import Procedure

from .forms import AppointmentUpdateForm, BookingRulesForm, ChannelForm, LoginForm

ROLE_GROUPS = ("doctor", "secretary")


def user_role(user) -> str:
    names = set(user.groups.values_list("name", flat=True))
    if "doctor" in names:
        return "doctor"
    if "secretary" in names:
        return "secretary"
    return "admin" if user.is_superuser else "staff"


def staff_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect(f"{reverse('panel:login')}?next={request.get_full_path()}")
        if not (user.is_staff or user.groups.filter(name__in=ROLE_GROUPS).exists()):
            return HttpResponseForbidden(_("You do not have access to the panel."))
        request.role = user_role(user)
        return view(request, *args, **kwargs)
    return wrapper


def admin_required(view):
    @wraps(view)
    @staff_required
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_superuser or request.role == "doctor"):
            return HttpResponseForbidden(_("Only the doctor or an administrator can change settings."))
        return view(request, *args, **kwargs)
    return wrapper


class LoginView(auth_views.LoginView):
    template_name = "panel/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@staff_required
def dashboard(request):
    today = timezone.localdate()
    week_end = today + dt.timedelta(days=7)
    qs = Appointment.objects.select_related("procedure")
    stats = {
        "today": qs.filter(preferred_date=today).active().count(),
        "pending": qs.filter(status=Appointment.Status.PENDING).count(),
        "week": qs.filter(preferred_date__range=(today, week_end)).active().count(),
        "unread": Thread.objects.filter(unread_for_staff__gt=0, status=Thread.Status.OPEN).count(),
    }
    top = (
        Appointment.objects.filter(created_at__gte=timezone.now() - dt.timedelta(days=30))
        .values("procedure__title_fa", "procedure__title_en", "procedure__title_ar")
        .annotate(n=Count("id")).order_by("-n")[:5]
    )
    return render(request, "panel/dashboard.html", {
        "stats": stats,
        "upcoming": qs.filter(preferred_date__gte=today).active().order_by("preferred_date", "time_slot")[:8],
        "pending": qs.filter(status=Appointment.Status.PENDING).order_by("created_at")[:6],
        "threads": Thread.objects.filter(status=Thread.Status.OPEN)[:6],
        "top": top,
        "today": today,
        "nav": "dashboard",
    })


# ---------------------------------------------------------------------------
# Appointments
# ---------------------------------------------------------------------------
def _filtered_appointments(request):
    qs = Appointment.objects.select_related("procedure", "handled_by")
    status = request.GET.get("status", "")
    when = request.GET.get("when", "")
    q = request.GET.get("q", "").strip()
    procedure = request.GET.get("procedure", "")
    today = timezone.localdate()
    if status in Appointment.Status.values:
        qs = qs.filter(status=status)
    if when == "today":
        qs = qs.filter(preferred_date=today)
    elif when == "week":
        qs = qs.filter(preferred_date__range=(today, today + dt.timedelta(days=7)))
    elif when == "upcoming":
        qs = qs.filter(preferred_date__gte=today)
    elif when == "past":
        qs = qs.filter(preferred_date__lt=today)
    if procedure.isdigit():
        qs = qs.filter(procedure_id=int(procedure))
    if q:
        qs = qs.filter(Q(full_name__icontains=q) | Q(phone__icontains=q) | Q(code__icontains=q))
    if when in {"today", "week", "upcoming"}:
        qs = qs.order_by("preferred_date", "time_slot")
    return qs


@staff_required
def appointments(request):
    qs = _filtered_appointments(request)
    page = Paginator(qs, 25).get_page(request.GET.get("page"))
    counts = dict(Appointment.objects.values_list("status").annotate(n=Count("id")))
    params = request.GET.copy()
    params.pop("page", None)
    return render(request, "panel/appointments.html", {
        "page": page,
        "statuses": Appointment.Status.choices,
        "counts": counts,
        "procedures": Procedure.objects.all(),
        "filters": request.GET,
        "querystring": params.urlencode(),
        "nav": "appointments",
    })


@staff_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment.objects.select_related("procedure", "handled_by"), pk=pk)
    old_status = appointment.status
    form = AppointmentUpdateForm(request.POST or None, instance=appointment)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            obj = form.save(commit=False)
            obj.handled_by = request.user
            obj.save()
            if obj.status != old_status:
                notify_booking(obj, Event.BOOKING_STATUS, actor=request.user.get_full_name() or request.user.username)
        messages.success(request, _("Appointment saved."))
        return redirect("panel:appointment_detail", pk=pk)
    others = Appointment.objects.filter(phone=appointment.phone).exclude(pk=pk)[:5]
    threads = Thread.objects.filter(visitor_phone=appointment.phone)[:3] if appointment.phone else []
    return render(request, "panel/appointment_detail.html", {
        "a": appointment, "form": form, "others": others, "threads": threads, "nav": "appointments",
    })


@staff_required
@require_POST
def appointment_status(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    status = request.POST.get("status")
    if status not in Appointment.Status.values:
        return JsonResponse({"ok": False}, status=400)
    if status != appointment.status:
        with transaction.atomic():
            appointment.status = status
            appointment.handled_by = request.user
            appointment.save(update_fields=["status", "handled_by", "updated_at"])
            notify_booking(appointment, Event.BOOKING_STATUS, actor=request.user.get_full_name() or request.user.username)
    return JsonResponse({"ok": True, "status": appointment.status, "label": appointment.get_status_display(),
                         "tone": appointment.status_tone})


@staff_required
def appointments_csv(request):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="appointments.csv"'
    response.write("﻿")  # Excel needs the BOM to read Persian correctly
    writer = csv.writer(response)
    writer.writerow([_("Tracking code"), _("Full name"), _("Mobile number"), _("Procedure"),
                     _("Date"), _("Gregorian date"), _("Time"), _("Status"), _("Note"), _("Created")])
    for a in _filtered_appointments(request)[:5000]:
        writer.writerow([
            a.code, a.full_name, a.phone, a.procedure.tr("title") if a.procedure else "",
            format_date(a.preferred_date, "fa", "short"), a.preferred_date.isoformat(), a.time_slot,
            a.get_status_display(), a.note, timezone.localtime(a.created_at).strftime("%Y-%m-%d %H:%M"),
        ])
    return response


# ---------------------------------------------------------------------------
# Chat inbox
# ---------------------------------------------------------------------------
def _threads_for(request):
    qs = Thread.objects.all()
    box = request.GET.get("box", "")
    if box in Thread.Recipient.values:
        qs = qs.filter(recipient=box)
    elif box == "mine" and request.role in Thread.Recipient.values:
        qs = qs.filter(recipient=request.role)
    if request.GET.get("status") == "closed":
        qs = qs.filter(status=Thread.Status.CLOSED)
    else:
        qs = qs.filter(status=Thread.Status.OPEN)
    return qs


@staff_required
def chats(request, pk=None):
    threads = _threads_for(request)[:100]
    thread = get_object_or_404(Thread, pk=pk) if pk else None
    if thread and thread.unread_for_staff:
        Thread.objects.filter(pk=thread.pk).update(unread_for_staff=0)
        thread.unread_for_staff = 0
    return render(request, "panel/chats.html", {
        "threads": threads,
        "thread": thread,
        "messages_list": thread.messages.all() if thread else [],
        "box": request.GET.get("box", ""),
        "nav": "chats",
    })


@staff_required
def chat_api(request, pk):
    """GET: new messages after ?after=id. POST: send a staff reply."""
    thread = get_object_or_404(Thread, pk=pk)
    if request.method == "POST":
        body = request.POST.get("body", "").strip()[:2000]
        if not body:
            return JsonResponse({"ok": False}, status=400)
        name = request.user.get_full_name() or request.user.username
        with transaction.atomic():
            msg = Message.objects.create(thread=thread, sender=Message.Sender.STAFF, staff_user=request.user,
                                         staff_name=name, body=body)
            Thread.objects.filter(pk=thread.pk).update(
                last_message_at=timezone.now(), unread_for_visitor=F("unread_for_visitor") + 1,
                unread_for_staff=0, assigned_to=thread.assigned_to or request.user,
            )
        return JsonResponse({"ok": True, "message": msg.as_dict()})
    after = request.GET.get("after", "0")
    new = thread.messages.filter(id__gt=int(after) if after.isdigit() else 0)
    if new and thread.unread_for_staff:
        Thread.objects.filter(pk=thread.pk).update(unread_for_staff=0)
    thread.refresh_from_db(fields=["page_context"])
    return JsonResponse({"ok": True, "messages": [m.as_dict() for m in new], "context": thread.page_context})


@staff_required
@require_POST
def chat_toggle(request, pk):
    thread = get_object_or_404(Thread, pk=pk)
    thread.status = Thread.Status.CLOSED if thread.status == Thread.Status.OPEN else Thread.Status.OPEN
    thread.save(update_fields=["status"])
    return redirect("panel:chat_detail", pk=pk)


@staff_required
def pulse(request):
    """Small JSON the panel polls to show live badges."""
    since = request.GET.get("since")
    new_bookings = 0
    if since:
        try:
            new_bookings = Appointment.objects.filter(created_at__gt=dt.datetime.fromisoformat(since)).count()
        except ValueError:
            pass
    return JsonResponse({
        "now": timezone.now().isoformat(),
        "unread_chats": Thread.objects.filter(unread_for_staff__gt=0, status=Thread.Status.OPEN).count(),
        "pending": Appointment.objects.filter(status=Appointment.Status.PENDING).count(),
        "new_bookings": new_bookings,
    })


# ---------------------------------------------------------------------------
# Settings: notification channels & booking rules
# ---------------------------------------------------------------------------
@admin_required
def settings_view(request):
    site = SiteSettings.load()
    rules = BookingRulesForm(request.POST or None, instance=site)
    if request.method == "POST" and rules.is_valid():
        rules.save()
        messages.success(request, _("Booking rules saved."))
        return redirect("panel:settings")
    channels = Channel.objects.annotate(
        sent=Count("logs", filter=Q(logs__ok=True)), failed=Count("logs", filter=Q(logs__ok=False))
    )
    return render(request, "panel/settings.html", {"channels": channels, "rules": rules, "nav": "settings"})


@admin_required
def channel_edit(request, pk=None):
    channel = get_object_or_404(Channel, pk=pk) if pk else None
    form = ChannelForm(request.POST or None, instance=channel)
    if request.method == "POST" and form.is_valid():
        channel = form.save()
        messages.success(request, _("Channel saved."))
        return redirect("panel:channel_edit", pk=channel.pk)
    webhook_url = absolute(channel.webhook_path()) if channel and channel.supports_replies else ""
    return render(request, "panel/channel_form.html", {
        "form": form, "channel": channel, "webhook_url": webhook_url,
        "logs": channel.logs.all()[:15] if channel else [], "nav": "settings",
    })


@admin_required
@require_POST
def channel_test(request, pk):
    channel = get_object_or_404(Channel, pk=pk)
    notice = Notice(event="test", title="پیام آزمایشی از سایت کلینیک",
                    lines=[("وضعیت", "اتصال برقرار است ✓"), ("کانال", channel.name)])
    logs = deliver(notice, only=channel)
    log = logs[0] if logs else None
    if log and log.ok:
        messages.success(request, _("Test message sent."))
    else:
        messages.error(request, _("Sending failed: %(detail)s") % {"detail": log.detail if log else "—"})
    return redirect("panel:channel_edit", pk=pk)


@admin_required
@require_POST
def channel_webhook(request, pk):
    """Register (or remove) the bot webhook so replies and buttons work."""
    channel = get_object_or_404(Channel, pk=pk, kind__in=["telegram", "bale"])
    if request.POST.get("action") == "delete":
        ok, data = bot_call(channel, "deleteWebhook", {})
    else:
        url = absolute(channel.webhook_path())
        if not url.startswith("https://"):
            messages.error(request, _("Webhooks need a public https address. Set SITE_BASE_URL in .env first."))
            return redirect("panel:channel_edit", pk=pk)
        ok, data = bot_call(channel, "setWebhook", {"url": url, "allowed_updates": ["message", "callback_query"]})
    if ok:
        messages.success(request, _("Bot connection updated."))
    else:
        messages.error(request, _("Sending failed: %(detail)s") % {"detail": str(data)[:300]})
    return redirect("panel:channel_edit", pk=pk)


@admin_required
@require_POST
def channel_delete(request, pk):
    get_object_or_404(Channel, pk=pk).delete()
    messages.success(request, _("Channel deleted."))
    return redirect("panel:settings")
