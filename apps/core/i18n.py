"""Helpers for the per-language model fields (``title_fa``, ``title_ar``, ``title_en``).

Each translatable field is stored once per language. ``TranslatedModel.tr()``
returns the value for the active language and falls back to Persian, then
to any language that has content, so a page never shows an empty heading.
"""
from django.conf import settings
from django.db import models
from django.utils.translation import get_language

LANG_CODES = [code for code, _ in settings.LANGUAGES]
FALLBACK_ORDER = ["fa", "en", "ar"]


def current_lang() -> str:
    lang = (get_language() or settings.LANGUAGE_CODE).split("-")[0]
    return lang if lang in LANG_CODES else settings.LANGUAGE_CODE


def is_rtl(lang: str | None = None) -> bool:
    return (lang or current_lang()) in settings.RTL_LANGUAGES


def translated_fields(name: str, field_cls=models.CharField, required_lang: str = "fa", **kwargs):
    """Return a dict ``{name_fa: Field, name_ar: Field, name_en: Field}``.

    Only the ``required_lang`` copy is mandatory; the others may be blank.
    Used with ``locals().update(...)`` inside a model body.
    """
    from django.utils.translation import gettext_lazy as _

    labels = {"fa": _("Persian"), "ar": _("Arabic"), "en": _("English")}
    verbose = kwargs.pop("verbose_name", name)
    fields = {}
    for code in LANG_CODES:
        opts = dict(kwargs)
        if code != required_lang:
            opts["blank"] = True
            if field_cls is models.CharField:
                opts.setdefault("default", "")
        fields[f"{name}_{code}"] = field_cls(verbose_name=f"{verbose} ({labels[code]})", **opts)
    return fields


class TranslatedModel(models.Model):
    class Meta:
        abstract = True

    def tr(self, name: str, lang: str | None = None) -> str:
        lang = lang or current_lang()
        value = getattr(self, f"{name}_{lang}", "") or ""
        if value:
            return value
        for code in FALLBACK_ORDER:
            value = getattr(self, f"{name}_{code}", "") or ""
            if value:
                return value
        return ""
