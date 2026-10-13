import datetime as dt

from django.conf import settings
from django.db.models import Prefetch
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.procedures.models import Category, Procedure

from .i18n import current_lang, is_rtl
from .models import SiteSettings

LANG_META = {
    "fa": {"native": "فارسی", "short": "فا"},
    "ar": {"native": "العربية", "short": "ع"},
    "en": {"native": "English", "short": "EN"},
}


def _js_config(site: SiteSettings, lang: str) -> dict:
    """Everything the front-end script needs: URLs, booking rules and UI strings."""
    today = timezone.localdate()
    return {
        "lang": lang,
        "dir": "rtl" if is_rtl(lang) else "ltr",
        "urls": {
            "slots": reverse("bookings:slots"),
            "submit": reverse("bookings:submit"),
            "chatState": reverse("chat:state"),
            "chatStart": reverse("chat:start"),
            "chatSend": reverse("chat:send"),
            "chatReset": reverse("chat:reset"),
        },
        "booking": {
            "today": today.isoformat(),
            "maxDate": (today + dt.timedelta(days=site.booking_days_ahead)).isoformat(),
            # Python weekday (Mon=0) → JS getDay (Sun=0)
            "closedDays": [(d + 1) % 7 for d in site.closed_weekday_list],
        },
        "t": {
            "pickDate": _("Choose a date"),
            "prevMonth": _("Previous month"),
            "nextMonth": _("Next month"),
            "closed": _("Closed"),
            "loadingSlots": _("Loading available times…"),
            "noSlots": _("No free time on this day. Please choose another day."),
            "pickDateFirst": _("Choose a date to see free times."),
            "required": _("This field is required."),
            "pickTime": _("Choose a time."),
            "network": _("Connection problem. Please try again."),
            "sending": _("Sending…"),
            "before": _("Before"),
            "after": _("After"),
            "compare": _("Drag to compare before and after"),
            "you": _("You"),
            "clinic": _("Clinic"),
            "doctor": _("Doctor"),
            "secretary": _("Secretary"),
            "reading": _("Section"),
            "today": _("Today"),
        },
    }


def site(request):
    lang = current_lang()
    path = request.path
    site_settings = SiteSettings.load()
    public = not path.startswith(("/panel", "/admin"))
    return {
        "clinic": site_settings,
        "LANG": lang,
        "DIR": "rtl" if is_rtl(lang) else "ltr",
        "IS_RTL": is_rtl(lang),
        "LANG_META": LANG_META,
        "LANG_CODES": [code for code, _name in settings.LANGUAGES],
        "DEMO_CONTENT": settings.DEMO_CONTENT,
        "RK_CONFIG": _js_config(site_settings, lang) if public else {},
        "NAV_CATEGORIES": (
            Category.objects.prefetch_related(
                Prefetch("procedures", queryset=Procedure.objects.published(), to_attr="live_procedures")
            )
            if public
            else []
        ),
    }
