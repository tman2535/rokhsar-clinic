from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.core.i18n import TranslatedModel, translated_fields

ICON_CHOICES = [
    ("nose", _("Nose")),
    ("face", _("Face")),
    ("eye", _("Eye")),
    ("body", _("Body")),
    ("syringe", _("Injection")),
    ("hair", _("Hair")),
    ("lips", _("Lips")),
    ("sparkle", _("Skin")),
]


class Category(TranslatedModel):
    slug = models.SlugField(_("Slug"), unique=True)
    locals().update(translated_fields("name", max_length=80, verbose_name=_("Name")))
    icon = models.CharField(_("Icon"), max_length=20, choices=ICON_CHOICES, default="face")
    order = models.PositiveSmallIntegerField(_("Order"), default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.tr("name")


class PublishedQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)


class Procedure(TranslatedModel):
    """A treatment the clinic offers (surgical or non-surgical)."""

    category = models.ForeignKey(Category, verbose_name=_("Category"), on_delete=models.PROTECT, related_name="procedures")
    slug = models.SlugField(_("Slug"), unique=True)
    icon = models.CharField(_("Icon"), max_length=20, choices=ICON_CHOICES, default="face")
    is_surgical = models.BooleanField(_("Surgical"), default=True)
    locals().update(translated_fields("title", max_length=120, verbose_name=_("Title")))
    locals().update(translated_fields("summary", max_length=300, verbose_name=_("Short summary")))
    locals().update(translated_fields("intro", models.TextField, verbose_name=_("Introduction")))
    locals().update(translated_fields("duration", max_length=80, verbose_name=_("Duration")))
    locals().update(translated_fields("anesthesia", max_length=80, verbose_name=_("Anesthesia")))
    locals().update(translated_fields("recovery", max_length=80, verbose_name=_("Back to routine")))
    locals().update(translated_fields("longevity", max_length=80, verbose_name=_("Result longevity")))
    locals().update(translated_fields("meta_description", max_length=170, verbose_name=_("SEO description")))
    cover = models.ImageField(_("Cover image"), upload_to="procedures/", blank=True)
    is_featured = models.BooleanField(_("Show on home page"), default=True)
    is_published = models.BooleanField(_("Published"), default=True)
    order = models.PositiveSmallIntegerField(_("Order"), default=0)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PublishedQuerySet.as_manager()

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("Procedure")
        verbose_name_plural = _("Procedures")

    def __str__(self):
        return self.tr("title")

    def get_absolute_url(self):
        return reverse("procedures:detail", kwargs={"slug": self.slug})


class ProcedureSection(TranslatedModel):
    """One chapter of a procedure page (mirrors a medical-society guide: candidates, risks …)."""

    KEY_CHOICES = [
        ("candidates", _("Is it right for me?")),
        ("consultation", _("Consultation")),
        ("questions", _("Questions to ask")),
        ("preparation", _("Preparation")),
        ("procedure", _("Procedure steps")),
        ("recovery", _("Recovery")),
        ("risks", _("Risks and safety")),
        ("results", _("Results")),
        ("cost", _("Cost")),
    ]
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name="sections")
    key = models.CharField(_("Section"), max_length=20, choices=KEY_CHOICES)
    locals().update(translated_fields("body", models.TextField, verbose_name=_("Text")))
    order = models.PositiveSmallIntegerField(_("Order"), default=0)

    class Meta:
        ordering = ["order", "id"]
        unique_together = [("procedure", "key")]
        verbose_name = _("Section")
        verbose_name_plural = _("Sections")

    def __str__(self):
        return f"{self.procedure} — {self.get_key_display()}"

    @property
    def anchor(self):
        return self.key


class FAQ(TranslatedModel):
    procedure = models.ForeignKey(
        Procedure, verbose_name=_("Procedure"), on_delete=models.CASCADE,
        null=True, blank=True, related_name="faqs",
        help_text=_("Leave empty for a general question shown on the home page."),
    )
    locals().update(translated_fields("question", max_length=255, verbose_name=_("Question")))
    locals().update(translated_fields("answer", models.TextField, verbose_name=_("Answer")))
    order = models.PositiveSmallIntegerField(_("Order"), default=0)
    is_published = models.BooleanField(_("Published"), default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQs")

    def __str__(self):
        return self.tr("question")


class ResultCase(TranslatedModel):
    """A before/after pair. Publish only with the patient's written consent."""

    procedure = models.ForeignKey(Procedure, verbose_name=_("Procedure"), on_delete=models.CASCADE, related_name="cases")
    locals().update(translated_fields("title", max_length=120, verbose_name=_("Title")))
    locals().update(translated_fields("caption", max_length=200, verbose_name=_("Caption")))
    before_image = models.ImageField(_("Before photo"), upload_to="cases/")
    after_image = models.ImageField(_("After photo"), upload_to="cases/")
    months_after = models.PositiveSmallIntegerField(_("Months after surgery"), default=6)
    patient_consent = models.BooleanField(_("Patient consent on file"), default=False)
    is_hero = models.BooleanField(_("Show in hero"), default=False)
    is_published = models.BooleanField(_("Published"), default=True)
    order = models.PositiveSmallIntegerField(_("Order"), default=0)

    objects = PublishedQuerySet.as_manager()

    class Meta:
        ordering = ["order", "-id"]
        verbose_name = _("Before / after case")
        verbose_name_plural = _("Before / after cases")

    def __str__(self):
        return self.tr("title") or str(self.procedure)
