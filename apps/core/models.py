from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext_lazy as _

from .i18n import TranslatedModel, translated_fields

WEEKDAYS = [
    (5, _("Saturday")),
    (6, _("Sunday")),
    (0, _("Monday")),
    (1, _("Tuesday")),
    (2, _("Wednesday")),
    (3, _("Thursday")),
    (4, _("Friday")),
]


class SiteSettings(TranslatedModel):
    """Single-row table holding the clinic's public details and booking rules."""

    locals().update(translated_fields("clinic_name", max_length=120, verbose_name=_("Clinic name")))
    locals().update(translated_fields("tagline", max_length=200, verbose_name=_("Tagline")))
    locals().update(translated_fields("doctor_name", max_length=120, verbose_name=_("Doctor name")))
    locals().update(translated_fields("doctor_title", max_length=200, verbose_name=_("Doctor speciality")))
    locals().update(translated_fields("doctor_bio", models.TextField, verbose_name=_("Doctor biography")))
    locals().update(translated_fields("address", max_length=255, verbose_name=_("Address")))
    locals().update(translated_fields("working_hours", max_length=200, verbose_name=_("Working hours")))

    doctor_photo = models.ImageField(_("Doctor photo"), upload_to="site/", blank=True)
    license_number = models.CharField(_("Medical council number"), max_length=40, blank=True)
    phone = models.CharField(_("Phone"), max_length=40, blank=True)
    whatsapp = models.CharField(_("WhatsApp number"), max_length=40, blank=True, help_text=_("International format, e.g. 989121234567"))
    instagram = models.CharField(_("Instagram username"), max_length=60, blank=True)
    telegram = models.CharField(_("Telegram username"), max_length=60, blank=True)
    email = models.EmailField(_("Email"), blank=True)
    map_url = models.URLField(_("Map link"), blank=True)

    years_experience = models.PositiveSmallIntegerField(_("Years of experience"), default=15)
    procedures_count = models.PositiveIntegerField(_("Procedures performed"), default=4000)
    satisfaction_rate = models.PositiveSmallIntegerField(_("Satisfaction rate (%)"), default=97)

    time_slots = models.CharField(
        _("Time slots"),
        max_length=255,
        default="10:00,10:30,11:00,11:30,12:00,16:00,16:30,17:00,17:30,18:00",
        help_text=_("Comma-separated, 24-hour format."),
    )
    slot_capacity = models.PositiveSmallIntegerField(_("Bookings per slot"), default=1)
    closed_weekdays = models.CharField(
        _("Closed weekdays"), max_length=20, default="4",
        help_text=_("Comma-separated Python weekday numbers (Monday=0 … Friday=4)."),
    )
    booking_days_ahead = models.PositiveSmallIntegerField(_("Bookable days ahead"), default=60)

    class Meta:
        verbose_name = _("Site settings")
        verbose_name_plural = _("Site settings")

    def __str__(self):
        return self.tr("clinic_name")

    CACHE_KEY = "site-settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete(self.CACHE_KEY)

    @classmethod
    def load(cls) -> "SiteSettings":
        obj = cache.get(cls.CACHE_KEY)
        if obj is None:
            obj, _created = cls.objects.get_or_create(
                pk=1,
                defaults={
                    "clinic_name_fa": "کلینیک رخسار",
                    "clinic_name_en": "Rokhsar Clinic",
                    "clinic_name_ar": "عيادة رخسار",
                },
            )
            cache.set(cls.CACHE_KEY, obj, 300)
        return obj

    # -- booking helpers --------------------------------------------------
    @property
    def slot_list(self) -> list[str]:
        return [s.strip() for s in self.time_slots.split(",") if s.strip()]

    @property
    def closed_weekday_list(self) -> list[int]:
        out = []
        for part in self.closed_weekdays.split(","):
            part = part.strip()
            if part.isdigit():
                out.append(int(part))
        return out


class Testimonial(TranslatedModel):
    name = models.CharField(_("Patient name"), max_length=80, help_text=_("Use initials if the patient prefers."))
    procedure = models.ForeignKey(
        "procedures.Procedure", verbose_name=_("Procedure"), on_delete=models.SET_NULL,
        null=True, blank=True, related_name="testimonials",
    )
    locals().update(translated_fields("text", models.TextField, verbose_name=_("Text")))
    rating = models.PositiveSmallIntegerField(_("Rating"), default=5)
    months_after = models.PositiveSmallIntegerField(_("Months after treatment"), default=6)
    is_published = models.BooleanField(_("Published"), default=True)
    order = models.PositiveSmallIntegerField(_("Order"), default=0)

    class Meta:
        ordering = ["order", "-id"]
        verbose_name = _("Testimonial")
        verbose_name_plural = _("Testimonials")

    def __str__(self):
        return self.name
