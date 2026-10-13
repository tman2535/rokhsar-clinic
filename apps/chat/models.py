import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Thread(models.Model):
    """A conversation between one visitor and the doctor or the secretary."""

    class Recipient(models.TextChoices):
        DOCTOR = "doctor", _("Doctor")
        SECRETARY = "secretary", _("Secretary")

    class Status(models.TextChoices):
        OPEN = "open", _("Open")
        CLOSED = "closed", _("Closed")

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    recipient = models.CharField(_("Addressed to"), max_length=10, choices=Recipient.choices, default=Recipient.SECRETARY)
    status = models.CharField(_("Status"), max_length=10, choices=Status.choices, default=Status.OPEN, db_index=True)
    visitor_name = models.CharField(_("Visitor name"), max_length=120)
    visitor_phone = models.CharField(_("Visitor phone"), max_length=20, blank=True)
    language = models.CharField(_("Language"), max_length=5, default="fa")
    # Latest page the visitor was on: {"title", "url", "type", "procedure", "section", ...}
    page_context = models.JSONField(_("Page context"), default=dict, blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_("Assigned to"), on_delete=models.SET_NULL,
        null=True, blank=True, related_name="chat_threads",
    )
    unread_for_staff = models.PositiveIntegerField(default=0)
    unread_for_visitor = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(_("Started"), auto_now_add=True)
    last_message_at = models.DateTimeField(_("Last message"), default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-last_message_at"]
        verbose_name = _("Conversation")
        verbose_name_plural = _("Conversations")

    def __str__(self):
        return f"#{self.pk} {self.visitor_name}"

    def get_panel_url(self):
        return reverse("panel:chat_detail", kwargs={"pk": self.pk})

    @property
    def tag(self) -> str:
        """Short tag used in Telegram so staff replies find their way back."""
        return f"#C{self.pk}"


class Message(models.Model):
    class Sender(models.TextChoices):
        VISITOR = "visitor", _("Visitor")
        STAFF = "staff", _("Staff")
        SYSTEM = "system", _("System")

    class Via(models.TextChoices):
        WEB = "web", _("Website")
        TELEGRAM = "telegram", _("Telegram")
        BALE = "bale", _("Bale")

    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=10, choices=Sender.choices)
    staff_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    staff_name = models.CharField(max_length=80, blank=True)
    body = models.TextField(max_length=2000)
    page_context = models.JSONField(default=dict, blank=True)
    via = models.CharField(max_length=10, choices=Via.choices, default=Via.WEB)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"{self.sender}: {self.body[:40]}"

    def as_dict(self) -> dict:
        return {
            "id": self.pk,
            "sender": self.sender,
            "name": self.staff_name if self.sender == "staff" else "",
            "body": self.body,
            "at": self.created_at.isoformat(),
            "context": self.page_context or {},
        }
