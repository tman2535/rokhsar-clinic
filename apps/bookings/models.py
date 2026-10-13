import secrets

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def new_code() -> str:
    return "RK-" + "".join(secrets.choice(CODE_ALPHABET) for _ in range(5))


class AppointmentQuerySet(models.QuerySet):
    def active(self):
        return self.exclude(status__in=[Appointment.Status.CANCELLED])


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Awaiting call")
        CONFIRMED = "confirmed", _("Confirmed")
        DONE = "done", _("Visited")
        NO_SHOW = "no_show", _("No-show")
        CANCELLED = "cancelled", _("Cancelled")

    code = models.CharField(_("Tracking code"), max_length=12, unique=True, default=new_code, editable=False)
    full_name = models.CharField(_("Full name"), max_length=120)
    phone = models.CharField(_("Mobile number"), max_length=20)
    procedure = models.ForeignKey(
        "procedures.Procedure", verbose_name=_("Procedure"), on_delete=models.SET_NULL,
        null=True, blank=True, related_name="appointments",
    )
    preferred_date = models.DateField(_("Preferred date"))
    time_slot = models.CharField(_("Time"), max_length=5)
    note = models.TextField(_("Note"), blank=True, max_length=600)

    status = models.CharField(_("Status"), max_length=12, choices=Status.choices, default=Status.PENDING, db_index=True)
    staff_note = models.TextField(_("Staff note"), blank=True)
    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_("Handled by"), on_delete=models.SET_NULL,
        null=True, blank=True, related_name="handled_appointments",
    )

    # Where the visitor was when they booked — shown to staff.
    source_url = models.CharField(_("Page"), max_length=300, blank=True)
    source_title = models.CharField(_("Page title"), max_length=200, blank=True)
    language = models.CharField(_("Language"), max_length=5, default="fa")
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(_("Created"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AppointmentQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Appointment")
        verbose_name_plural = _("Appointments")
        indexes = [models.Index(fields=["preferred_date", "time_slot"])]

    def __str__(self):
        return f"{self.code} · {self.full_name}"

    def get_panel_url(self):
        return reverse("panel:appointment_detail", kwargs={"pk": self.pk})

    @property
    def status_tone(self) -> str:
        return {
            "pending": "warn",
            "confirmed": "info",
            "done": "ok",
            "no_show": "muted",
            "cancelled": "danger",
        }[self.status]
