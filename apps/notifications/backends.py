"""Senders for each channel type. Each returns (ok, detail)."""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

import requests
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger("apps.notifications")

TIMEOUT = 12


@dataclass
class Notice:
    """A channel-agnostic notification."""

    event: str
    title: str
    lines: list[tuple[str, str]] = field(default_factory=list)  # (label, value)
    body: str = ""            # free text (e.g. the chat message)
    footer: str = ""          # e.g. "Reply to this message to answer"
    tag: str = ""             # "#C12" / "#B34" — lets bot replies find the record
    url: str = ""             # absolute panel URL
    buttons: list[list[dict]] = field(default_factory=list)  # Telegram inline keyboard
    data: dict = field(default_factory=dict)  # raw data for webhooks

    # -- renderers ------------------------------------------------------
    def as_text(self) -> str:
        parts = [f"{self.title} {self.tag}".strip()]
        parts += [f"{label}: {value}" for label, value in self.lines if value]
        if self.body:
            parts += ["", f"«{self.body}»"]
        if self.footer:
            parts += ["", self.footer]
        if self.url:
            parts += [self.url]
        return "\n".join(parts)

    def as_html(self) -> str:
        from html import escape

        parts = [f"<b>{escape(self.title)}</b> {escape(self.tag)}".strip()]
        parts += [f"{escape(label)}: <b>{escape(str(value))}</b>" for label, value in self.lines if value]
        if self.body:
            parts += ["", f"<blockquote>{escape(self.body)}</blockquote>"]
        if self.footer:
            parts += ["", f"<i>{escape(self.footer)}</i>"]
        return "\n".join(parts)


def _session(channel) -> requests.Session:
    s = requests.Session()
    if channel.proxy_url:
        s.proxies = {"http": channel.proxy_url, "https": channel.proxy_url}
    return s


def bot_api_base(channel) -> str:
    if channel.api_base:
        return channel.api_base.rstrip("/")
    return "https://tapi.bale.ai" if channel.kind == "bale" else "https://api.telegram.org"


def bot_call(channel, method: str, payload: dict) -> tuple[bool, dict | str]:
    """Call a Telegram-compatible Bot API (Telegram and Bale share the same shape)."""
    url = f"{bot_api_base(channel)}/bot{channel.token}/{method}"
    try:
        resp = _session(channel).post(url, json=payload, timeout=TIMEOUT)
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        return False, f"{type(exc).__name__}: {exc}"
    return bool(data.get("ok")), data


def _https_url(url: str) -> bool:
    return url.startswith("https://")


def send_bot(channel, notice: Notice) -> tuple[bool, str]:
    payload = {"chat_id": channel.target, "disable_web_page_preview": True}
    if channel.kind == "telegram":
        payload.update(text=notice.as_html(), parse_mode="HTML")
    else:  # Bale: plain text is the safest common denominator
        payload.update(text=notice.as_text())
    keyboard = [row[:] for row in notice.buttons] if channel.allow_replies else []
    if notice.url and _https_url(notice.url):
        keyboard.append([{"text": "پنل مدیریت", "url": notice.url}])
    if keyboard:
        payload["reply_markup"] = {"inline_keyboard": keyboard}
    ok, data = bot_call(channel, "sendMessage", payload)
    return ok, str(data)[:500]


def send_eitaa(channel, notice: Notice) -> tuple[bool, str]:
    base = (channel.api_base or "https://eitaayar.ir/api").rstrip("/")
    try:
        resp = _session(channel).post(
            f"{base}/{channel.token}/sendMessage",
            data={"chat_id": channel.target, "text": notice.as_text()},
            timeout=TIMEOUT,
        )
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        return False, f"{type(exc).__name__}: {exc}"
    return bool(data.get("ok")), str(data)[:500]


def send_whatsapp(channel, notice: Notice) -> tuple[bool, str]:
    base = (channel.api_base or "https://graph.facebook.com/v21.0").rstrip("/")
    to = re.sub(r"\D", "", channel.target)
    try:
        resp = _session(channel).post(
            f"{base}/{channel.sender_id}/messages",
            headers={"Authorization": f"Bearer {channel.token}"},
            json={"messaging_product": "whatsapp", "to": to, "type": "text",
                  "text": {"body": notice.as_text()[:4000], "preview_url": False}},
            timeout=TIMEOUT,
        )
        return resp.ok, resp.text[:500]
    except requests.RequestException as exc:
        return False, f"{type(exc).__name__}: {exc}"


def send_email(channel, notice: Notice) -> tuple[bool, str]:
    recipients = [a.strip() for a in channel.target.split(",") if a.strip()]
    if not recipients:
        return False, "No recipients"
    try:
        sent = send_mail(f"{notice.title} {notice.tag}".strip(), notice.as_text(),
                         settings.DEFAULT_FROM_EMAIL, recipients)
    except Exception as exc:  # SMTP errors vary widely
        return False, f"{type(exc).__name__}: {exc}"
    return bool(sent), f"sent={sent}"


def send_webhook(channel, notice: Notice) -> tuple[bool, str]:
    headers = {"Content-Type": "application/json"}
    if channel.token:
        headers["Authorization"] = f"Bearer {channel.token}"
    body = {
        "event": notice.event, "title": notice.title, "tag": notice.tag,
        "text": notice.as_text(), "url": notice.url, "data": notice.data,
    }
    try:
        resp = _session(channel).post(channel.target, json=body, headers=headers, timeout=TIMEOUT)
        return resp.ok, f"HTTP {resp.status_code}"
    except requests.RequestException as exc:
        return False, f"{type(exc).__name__}: {exc}"


SENDERS = {
    "telegram": send_bot,
    "bale": send_bot,
    "eitaa": send_eitaa,
    "whatsapp": send_whatsapp,
    "email": send_email,
    "webhook": send_webhook,
}
