import datetime as dt

from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import SiteSettings
from apps.core.utils import is_valid_phone, normalize_phone
from apps.procedures.models import Procedure

from .models import Appointment


def slot_taken_count(date: dt.date, slot: str) -> int:
    return Appointment.objects.active().filter(preferred_date=date, time_slot=slot).count()


def slot_states(date: dt.date) -> list[dict]:
    """Every slot for a date with whether it can still be booked."""
    cfg = SiteSettings.load()
    now = timezone.localtime()
    out = []
    for slot in cfg.slot_list:
        available = slot_taken_count(date, slot) < cfg.slot_capacity
        if date == now.date():
            hh, mm = (int(x) for x in slot.split(":"))
            if (hh, mm) <= (now.hour + 1, now.minute):  # need at least an hour's notice
                available = False
        out.append({"time": slot, "available": available})
    return out


def date_is_bookable(date: dt.date) -> bool:
    cfg = SiteSettings.load()
    today = timezone.localdate()
    return (
        today <= date <= today + dt.timedelta(days=cfg.booking_days_ahead)
        and date.weekday() not in cfg.closed_weekday_list
    )


class BookingForm(forms.ModelForm):
    # Honeypot: real people never see or fill this field.
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Appointment
        fields = ["full_name", "phone", "procedure", "preferred_date", "time_slot", "note", "source_url", "source_title"]
        widgets = {
            "full_name": forms.TextInput(attrs={"autocomplete": "name", "maxlength": 120}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel", "dir": "ltr", "maxlength": 20}),
            "preferred_date": forms.HiddenInput(),
            "time_slot": forms.HiddenInput(),
            "note": forms.Textarea(attrs={"rows": 2, "maxlength": 600}),
            "source_url": forms.HiddenInput(),
            "source_title": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["procedure"].queryset = Procedure.objects.published().select_related("category")
        self.fields["procedure"].required = True
        self.fields["procedure"].empty_label = _("Choose a treatment")
        self.fields["procedure"].label_from_instance = lambda obj: obj.tr("title")
        self.fields["note"].required = False

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("spam")
        return ""

    def clean_full_name(self):
        name = " ".join(self.cleaned_data["full_name"].split())
        if len(name) < 3:
            raise forms.ValidationError(_("Please write your full name."))
        return name

    def clean_phone(self):
        phone = normalize_phone(self.cleaned_data["phone"])
        if not is_valid_phone(phone):
            raise forms.ValidationError(_("Enter a valid mobile number, e.g. 09121234567."))
        return phone

    def clean_preferred_date(self):
        date = self.cleaned_data["preferred_date"]
        if not date_is_bookable(date):
            raise forms.ValidationError(_("The clinic is not taking appointments on this day."))
        return date

    def clean(self):
        data = super().clean()
        date, slot = data.get("preferred_date"), data.get("time_slot")
        if date and slot:
            states = {s["time"]: s["available"] for s in slot_states(date)}
            if slot not in states:
                self.add_error("time_slot", _("Choose one of the listed times."))
            elif not states[slot]:
                self.add_error("time_slot", _("This time was just taken. Please pick another."))
        return data
