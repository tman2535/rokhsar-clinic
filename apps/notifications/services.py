"""Build notifications for clinic events and fan them out to every active channel.

Sending runs after the database transaction commits and, by default, in a
background thread, so the visitor's form submission answers instantly even
if a messenger API is slow or unreachable.
"""
from __future__ import annotations

import logging
import threading

from django.conf import settings
from django.db import close_old_connections, transaction
from django.utils import translation

from apps.core.jalali import format_date, localize_digits

from .backends import SENDERS, Notice
from .models import Channel, DeliveryLog, Event

logger = logging.getLogger("apps.notifications")

STAFF_LANG = "fa"  # clinic staff read notifications in Persian


def absolute(path: str) -> str:
    return settings.SITE_BASE_URL.rstrip("/") + path


def deliver(notice: Notice, exclude_channel_id: int | None = None,
            only: Channel | None = None) -> list[DeliveryLog]:
    """Send synchronously to all channels subscribed to the event.

    ``only`` sends to that single channel regardless of its event filter
    (used by the panel's "send test message" button).
    """
    logs = []
    channels = [only] if only else Channel.objects.filter(is_active=True)
    for channel in channels:
        if not only and (channel.pk == exclude_channel_id or not channel.wants(notice.event)):
            continue
        sender = SENDERS.get(channel.kind)
        if not sender:
            continue
        try:
            ok, detail = sender(channel, notice)
        except Exception as exc:  # never let one channel break the others
            logger.exception("Notification via %s failed", channel)
            ok, detail = False, f"{type(exc).__name__}: {exc}"
        logs.append(DeliveryLog.objects.create(channel=channel, event=notice.event, ok=ok, detail=detail[:2000]))
    return logs


def dispatch(notice: Notice, exclude_channel_id: int | None = None) -> None:
    """Queue delivery after commit; run in a thread unless NOTIFY_ASYNC is off."""

    def run():
        try:
            deliver(notice, exclude_channel_id)
        finally:
            close_old_connections()

    def start():
        if getattr(settings, "NOTIFY_ASYNC", True):
            threading.Thread(target=run, daemon=True).start()
        else:
            deliver(notice, exclude_channel_id)

    transaction.on_commit(start)


# ---------------------------------------------------------------------------
# Event builders
# ---------------------------------------------------------------------------
def _fa(value) -> str:
    return localize_digits(value, STAFF_LANG)


def booking_notice(appointment, event: str = Event.BOOKING_NEW, actor: str = "") -> Notice:
    with translation.override(STAFF_LANG):
        procedure = appointment.procedure.tr("title", STAFF_LANG) if appointment.procedure else "—"
        when = f"{format_date(appointment.preferred_date, STAFF_LANG)} — ساعت {_fa(appointment.time_slot)}"
        if event == Event.BOOKING_NEW:
            title = "درخواست نوبت جدید"
            lines = [
                ("نام", appointment.full_name),
                ("موبایل", appointment.phone),
                ("خدمت", procedure),
                ("زمان پیشنهادی", when),
                ("از صفحه", appointment.source_title),
                ("یادداشت", appointment.note),
                ("کد پیگیری", appointment.code),
            ]
        else:
            title = "وضعیت نوبت تغییر کرد"
            lines = [
                ("نام", appointment.full_name),
                ("خدمت", procedure),
                ("زمان", when),
                ("وضعیت جدید", str(appointment.get_status_display())),
                ("توسط", actor),
            ]
        buttons = []
        if appointment.status == "pending":
            buttons = [[
                {"text": "✓ تأیید نوبت", "callback_data": f"ap:{appointment.pk}:confirmed"},
                {"text": "✕ لغو", "callback_data": f"ap:{appointment.pk}:cancelled"},
            ]]
        return Notice(
            event=event, title=title, lines=lines, tag=f"#B{appointment.pk}",
            url=absolute(appointment.get_panel_url()), buttons=buttons,
            data={
                "id": appointment.pk, "code": appointment.code, "name": appointment.full_name,
                "phone": appointment.phone, "procedure": procedure,
                "date": appointment.preferred_date.isoformat(), "time": appointment.time_slot,
                "status": appointment.status, "page": appointment.source_url,
            },
        )


def context_label(ctx: dict) -> str:
    """Human-readable 'where is the visitor' line for staff."""
    if not ctx:
        return ""
    parts = [ctx.get("title") or ctx.get("url") or ""]
    if ctx.get("section"):
        parts.append(f"بخش «{ctx['section']}»")
    return " — ".join(p for p in parts if p)


def chat_notice(message, is_new: bool) -> Notice:
    thread = message.thread
    with translation.override(STAFF_LANG):
        recipient = "دکتر" if thread.recipient == "doctor" else "منشی"
        title = "گفتگوی جدید از وب‌سایت" if is_new else "پیام تازه در گفتگو"
        lines = [
            ("برای", recipient),
            ("از طرف", thread.visitor_name),
            ("موبایل", thread.visitor_phone),
            ("در حال دیدن", context_label(message.page_context or thread.page_context)),
        ]
        return Notice(
            event=Event.CHAT_NEW if is_new else Event.CHAT_MESSAGE,
            title=title, lines=lines, body=message.body, tag=thread.tag,
            footer="برای پاسخ، روی همین پیام «Reply» بزنید.",
            url=absolute(thread.get_panel_url()),
            data={
                "thread": thread.pk, "recipient": thread.recipient, "name": thread.visitor_name,
                "phone": thread.visitor_phone, "message": message.body,
                "page": message.page_context or thread.page_context,
            },
        )


def notify_booking(appointment, event: str = Event.BOOKING_NEW, actor: str = "",
                   exclude_channel_id: int | None = None) -> None:
    dispatch(booking_notice(appointment, event, actor), exclude_channel_id)


def notify_chat(message, is_new: bool) -> None:
    dispatch(chat_notice(message, is_new))
