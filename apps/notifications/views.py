"""Inbound webhook for Telegram / Bale bots.

What staff can do from inside the messenger:
  * /start or /id                → the bot replies with this chat's ID (for setup)
  * Reply to a "#C12" message    → the text is posted into website conversation 12
  * Tap ✓ / ✕ under "#B34"       → appointment 34 is confirmed / cancelled
"""
from __future__ import annotations

import json
import logging
import re

from django.db import transaction
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.crypto import constant_time_compare
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.bookings.models import Appointment
from apps.chat.models import Message, Thread

from .backends import bot_call
from .models import Channel, Event
from .services import notify_booking

logger = logging.getLogger("apps.notifications")

THREAD_TAG = re.compile(r"#C(\d+)")
STATUS_LABELS = {"confirmed": "تأیید شد ✓", "cancelled": "لغو شد ✕"}


def _same_chat(channel: Channel, chat_id) -> bool:
    return str(chat_id).strip() == str(channel.target).strip()


def _sender_name(user: dict) -> str:
    name = " ".join(filter(None, [user.get("first_name"), user.get("last_name")])).strip()
    return name or user.get("username") or "Staff"


@csrf_exempt
@require_POST
def bot_webhook(request, pk: int, secret: str):
    channel = get_object_or_404(Channel, pk=pk, kind__in=["telegram", "bale"])
    if not constant_time_compare(secret, channel.webhook_secret):
        return HttpResponseForbidden()
    try:
        update = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return HttpResponse(status=400)

    if "callback_query" in update:
        _handle_callback(channel, update["callback_query"])
    elif "message" in update:
        _handle_message(channel, update["message"])
    return JsonResponse({"ok": True})


def _handle_message(channel: Channel, msg: dict) -> None:
    chat_id = msg.get("chat", {}).get("id")
    text = (msg.get("text") or "").strip()

    if text.split("@")[0] in {"/start", "/id"}:
        bot_call(channel, "sendMessage", {
            "chat_id": chat_id,
            "text": f"شناسهٔ این چت: {chat_id}\nاین عدد را در پنل، در فیلد «گیرنده» همین کانال وارد کنید.",
        })
        return

    if not channel.allow_replies or not _same_chat(channel, chat_id) or not text:
        return
    replied = msg.get("reply_to_message") or {}
    match = THREAD_TAG.search(replied.get("text") or replied.get("caption") or "")
    if not match:
        return
    thread = Thread.objects.filter(pk=int(match.group(1))).first()
    if not thread:
        return
    with transaction.atomic():
        Message.objects.create(
            thread=thread, sender=Message.Sender.STAFF, body=text[:2000],
            staff_name=_sender_name(msg.get("from", {})),
            via=Message.Via.TELEGRAM if channel.kind == "telegram" else Message.Via.BALE,
        )
        Thread.objects.filter(pk=thread.pk).update(
            last_message_at=timezone.now(),
            unread_for_visitor=thread.unread_for_visitor + 1,
            unread_for_staff=0,
            status=Thread.Status.OPEN,
        )
    bot_call(channel, "sendMessage", {
        "chat_id": chat_id, "text": f"پاسخ برای {thread.tag} ارسال شد ✓",
        "reply_to_message_id": msg.get("message_id"),
    })


def _handle_callback(channel: Channel, cq: dict) -> None:
    message = cq.get("message") or {}
    chat_id = message.get("chat", {}).get("id")
    data = cq.get("data") or ""
    answer = {"callback_query_id": cq.get("id")}

    if not channel.allow_replies or not _same_chat(channel, chat_id):
        bot_call(channel, "answerCallbackQuery", {**answer, "text": "دسترسی ندارید."})
        return

    parts = data.split(":")
    if len(parts) != 3 or parts[0] != "ap" or parts[2] not in STATUS_LABELS:
        bot_call(channel, "answerCallbackQuery", answer)
        return

    appointment = Appointment.objects.filter(pk=int(parts[1])).first() if parts[1].isdigit() else None
    if not appointment:
        bot_call(channel, "answerCallbackQuery", {**answer, "text": "نوبت پیدا نشد."})
        return

    actor = _sender_name(cq.get("from", {}))
    with transaction.atomic():
        appointment.status = parts[2]
        stamp = f"[{timezone.localtime():%Y-%m-%d %H:%M}] {actor} از طریق ربات: {STATUS_LABELS[parts[2]]}"
        appointment.staff_note = (appointment.staff_note + "\n" + stamp).strip()
        appointment.save(update_fields=["status", "staff_note", "updated_at"])
        notify_booking(appointment, Event.BOOKING_STATUS, actor=actor, exclude_channel_id=channel.pk)

    bot_call(channel, "answerCallbackQuery", {**answer, "text": STATUS_LABELS[parts[2]]})
    # Replace the buttons with the outcome so nobody taps twice.
    bot_call(channel, "editMessageReplyMarkup", {
        "chat_id": chat_id, "message_id": message.get("message_id"),
        "reply_markup": {"inline_keyboard": [[{"text": f"{STATUS_LABELS[parts[2]]} — {actor}", "callback_data": "noop"}]]},
    })
