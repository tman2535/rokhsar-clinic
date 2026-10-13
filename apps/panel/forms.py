from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

from apps.bookings.models import Appointment
from apps.core.models import SiteSettings
from apps.notifications.models import Channel, Event


class StyledMixin:
    """Give every text-like widget the site's .input class."""

    def style_fields(self):
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple, forms.HiddenInput)):
                continue
            css = widget.attrs.get("class", "")
            if "input" not in css.split():
                widget.attrs["class"] = (css + " input").strip()


class LoginForm(AuthenticationForm):
    username = forms.CharField(label=_("Username"), widget=forms.TextInput(attrs={"autofocus": True, "autocomplete": "username", "dir": "ltr"}))
    password = forms.CharField(label=_("Password"), strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "current-password", "dir": "ltr"}))


class AppointmentUpdateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["status", "preferred_date", "time_slot", "staff_note"]
        widgets = {
            "preferred_date": forms.DateInput(attrs={"type": "date", "class": "input"}, format="%Y-%m-%d"),
            "time_slot": forms.TextInput(attrs={"dir": "ltr", "placeholder": "10:30", "maxlength": 5, "class": "input input--ltr"}),
            "staff_note": forms.Textarea(attrs={"rows": 4, "class": "input"}),
        }


class ChannelForm(StyledMixin, forms.ModelForm):
    events = forms.MultipleChoiceField(
        label=_("Send for"), choices=Event.choices, widget=forms.CheckboxSelectMultiple, required=False,
    )

    class Meta:
        model = Channel
        fields = ["name", "kind", "is_active", "events", "token", "target", "sender_id", "api_base", "proxy_url", "allow_replies"]
        widgets = {
            "token": forms.PasswordInput(render_value=True, attrs={"dir": "ltr", "autocomplete": "off"}),
            "target": forms.TextInput(attrs={"dir": "ltr"}),
            "sender_id": forms.TextInput(attrs={"dir": "ltr"}),
            "api_base": forms.URLInput(attrs={"dir": "ltr", "placeholder": "https://"}),
            "proxy_url": forms.TextInput(attrs={"dir": "ltr", "placeholder": "http://host:port"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.initial.setdefault("events", [Event.BOOKING_NEW, Event.CHAT_NEW, Event.CHAT_MESSAGE])
        self.style_fields()

    def clean(self):
        data = super().clean()
        kind, token, target = data.get("kind"), data.get("token"), data.get("target")
        if kind in {"telegram", "bale", "eitaa", "whatsapp"} and not token:
            self.add_error("token", _("This channel type needs a token."))
        if kind in {"email", "webhook", "whatsapp", "eitaa"} and not target:
            self.add_error("target", _("Enter where messages should go."))
        if kind == "whatsapp" and not data.get("sender_id"):
            self.add_error("sender_id", _("WhatsApp needs the phone-number ID."))
        if kind == "webhook" and target and not target.startswith(("http://", "https://")):
            self.add_error("target", _("Enter a full URL starting with https://"))
        return data


class BookingRulesForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = ["time_slots", "slot_capacity", "closed_weekdays", "booking_days_ahead", "phone", "whatsapp", "instagram", "telegram"]
        widgets = {f: forms.TextInput(attrs={"dir": "ltr"}) for f in ["time_slots", "closed_weekdays", "phone", "whatsapp", "instagram", "telegram"]}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_fields()
