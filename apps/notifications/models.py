import secrets

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Event(models.TextChoices):
    BOOKING_NEW = "booking_new", _("New appointment request")
    BOOKING_STATUS = "booking_status", _("Appointment status changed")
    CHAT_NEW = "chat_new", _("New conversation")
    CHAT_MESSAGE = "chat_message", _("New visitor message")


def _secret():
    return secrets.token_urlsafe(24)


class Channel(models.Model):
    """Somewhere the clinic wants to be told about new requests."""

    class Kind(models.TextChoices):
        TELEGRAM = "telegram", _("Telegram bot")
        BALE = "bale", _("Bale bot")
        EITAA = "eitaa", _("Eitaa (Eitaayar)")
        WHATSAPP = "whatsapp", _("WhatsApp Cloud API")
        EMAIL = "email", _("Email")
        WEBHOOK = "webhook", _("Webhook (n8n, Make, Zapier …)")

    name = models.CharField(_("Name"), max_length=80)
    kind = models.CharField(_("Type"), max_length=12, choices=Kind.choices)
    is_active = models.BooleanField(_("Active"), default=True)
    events = models.JSONField(_("Events"), default=list, blank=True)

    token = models.CharField(
        _("Token / API key"), max_length=255, blank=True,
        help_text=_("Bot token for Telegram/Bale, API token for Eitaayar, access token for WhatsApp."),
    )
    target = models.CharField(
        _("Recipient"), max_length=255, blank=True,
        help_text=_("Chat ID (Telegram/Bale/Eitaa), phone number (WhatsApp), addresses (email, comma-separated) or URL (webhook)."),
    )
    sender_id = models.CharField(
        _("Sender ID"), max_length=80, blank=True,
        help_text=_("WhatsApp only: phone-number ID from Meta."),
    )
    api_base = models.URLField(
        _("API address"), blank=True,
        help_text=_("Optional. A relay address if the official API is unreachable from your server."),
    )
    proxy_url = models.CharField(
        _("HTTP proxy"), max_length=255, blank=True,
        help_text=_("Optional, e.g. http://user:pass@host:port"),
    )
    allow_replies = models.BooleanField(
        _("Allow replies from the bot"), default=True,
        help_text=_("Telegram/Bale: answer chats and confirm appointments right inside the messenger."),
    )
    webhook_secret = models.CharField(max_length=64, default=_secret, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Notification channel")
        verbose_name_plural = _("Notification channels")

    def __str__(self):
        return f"{self.name} ({self.get_kind_display()})"

    def wants(self, event: str) -> bool:
        return self.is_active and event in (self.events or [])

    @property
    def supports_replies(self) -> bool:
        return self.kind in {self.Kind.TELEGRAM, self.Kind.BALE}

    def webhook_path(self) -> str:
        return reverse("notifications:bot_webhook", kwargs={"pk": self.pk, "secret": self.webhook_secret})


class DeliveryLog(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="logs")
    event = models.CharField(max_length=20, choices=Event.choices)
    ok = models.BooleanField(default=False)
    detail = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Delivery log")
        verbose_name_plural = _("Delivery logs")
