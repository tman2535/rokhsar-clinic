"""Visitor-side chat API (JSON). The visitor is identified by their session."""
import json

from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_POST

from apps.core.i18n import current_lang
from apps.core.utils import client_ip, is_valid_phone, normalize_phone, rate_limited
from apps.notifications.services import notify_chat

from .models import Message, Thread

SESSION_KEY = "chat_thread_id"
CONTEXT_KEYS = {"title", "url", "type", "procedure", "category", "section", "lang"}


def clean_context(raw) -> dict:
    """Keep only known keys, short strings — this is shown to staff verbatim."""
    if not isinstance(raw, dict):
        return {}
    out = {}
    for key in CONTEXT_KEYS:
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            out[key] = value.strip()[:200]
    return out


def _payload(request) -> dict:
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (ValueError, UnicodeDecodeError):
        return {}


def _thread(request) -> Thread | None:
    pk = request.session.get(SESSION_KEY)
    return Thread.objects.filter(pk=pk).first() if pk else None


def _state(thread: Thread, after: int = 0) -> dict:
    messages = thread.messages.filter(id__gt=after).exclude(sender=Message.Sender.SYSTEM)
    return {
        "ok": True,
        "thread": {
            "recipient": thread.recipient,
            "status": thread.status,
            "name": thread.visitor_name,
        },
        "unread": thread.unread_for_visitor,
        "messages": [m.as_dict() for m in messages[:200]],
    }


@require_GET
def state(request):
    thread = _thread(request)
    if not thread:
        return JsonResponse({"ok": True, "thread": None, "messages": [], "unread": 0})
    after = request.GET.get("after", "0")
    data = _state(thread, int(after) if after.isdigit() else 0)
    if request.GET.get("seen") == "1" and thread.unread_for_visitor:
        Thread.objects.filter(pk=thread.pk).update(unread_for_visitor=0)
        data["unread"] = 0
    return JsonResponse(data)


@require_POST
def start(request):
    if rate_limited(f"chat-start:{client_ip(request)}", limit=5, window=3600):
        return JsonResponse({"ok": False, "error": _("Too many conversations. Please call the clinic.")}, status=429)
    data = _payload(request)
    name = " ".join(str(data.get("name", "")).split())[:120]
    phone = normalize_phone(str(data.get("phone", "")))
    body = str(data.get("body", "")).strip()[:2000]
    recipient = data.get("recipient") if data.get("recipient") in Thread.Recipient.values else Thread.Recipient.SECRETARY

    errors = {}
    if len(name) < 2:
        errors["name"] = _("Please write your name.")
    if phone and not is_valid_phone(phone):
        errors["phone"] = _("Enter a valid mobile number, e.g. 09121234567.")
    if not body:
        errors["body"] = _("Write your message.")
    if errors:
        return JsonResponse({"ok": False, "errors": errors}, status=400)

    context = clean_context(data.get("context"))
    with transaction.atomic():
        thread = Thread.objects.create(
            recipient=recipient, visitor_name=name, visitor_phone=phone,
            language=current_lang(), page_context=context, unread_for_staff=1,
        )
        message = Message.objects.create(thread=thread, sender=Message.Sender.VISITOR, body=body, page_context=context)
        notify_chat(message, is_new=True)
    request.session[SESSION_KEY] = thread.pk
    return JsonResponse(_state(thread))


@require_POST
def send(request):
    thread = _thread(request)
    if not thread:
        return JsonResponse({"ok": False, "error": "no-thread"}, status=404)
    if rate_limited(f"chat-send:{thread.pk}", limit=30, window=600):
        return JsonResponse({"ok": False, "error": _("You are sending messages too quickly.")}, status=429)
    data = _payload(request)
    body = str(data.get("body", "")).strip()[:2000]
    if not body:
        return JsonResponse({"ok": False, "errors": {"body": _("Write your message.")}}, status=400)
    context = clean_context(data.get("context"))
    with transaction.atomic():
        message = Message.objects.create(thread=thread, sender=Message.Sender.VISITOR, body=body, page_context=context)
        Thread.objects.filter(pk=thread.pk).update(
            last_message_at=timezone.now(), unread_for_staff=F("unread_for_staff") + 1,
            status=Thread.Status.OPEN, page_context=context or thread.page_context,
        )
        notify_chat(message, is_new=False)
    return JsonResponse({"ok": True, "message": message.as_dict()})


@require_POST
def reset(request):
    """Start over (e.g. to write to the other recipient)."""
    request.session.pop(SESSION_KEY, None)
    return JsonResponse({"ok": True})
