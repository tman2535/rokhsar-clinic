"""End-to-end behaviour of the public site, booking, chat, panel and bot webhook."""
import datetime as dt
import json
from unittest import mock

from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone, translation

from apps.bookings.models import Appointment
from apps.chat.models import Message, Thread
from apps.core.jalali import format_date, gregorian_to_jalali, jalali_to_gregorian
from apps.core.models import SiteSettings
from apps.notifications.models import Channel, DeliveryLog
from apps.procedures.models import Procedure


def next_open_day(after_days=2):
    cfg = SiteSettings.load()
    day = timezone.localdate() + dt.timedelta(days=after_days)
    while day.weekday() in cfg.closed_weekday_list:
        day += dt.timedelta(days=1)
    return day


class FakeResponse:
    ok = True
    status_code = 200
    text = '{"ok": true}'

    def json(self):
        return {"ok": True, "result": {"message_id": 1}}


@override_settings(NOTIFY_ASYNC=False, SITE_BASE_URL="https://clinic.example")
class ClinicTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", verbosity=0, stdout=open("/dev/null", "w"))
        cls.rhino = Procedure.objects.get(slug="rhinoplasty")
        cls.channel = Channel.objects.create(
            name="Clinic group", kind="telegram", token="123:ABC", target="-1001",
            events=["booking_new", "booking_status", "chat_new", "chat_message"],
        )

    def setUp(self):
        from django.core.cache import cache
        cache.clear()

    # -- calendar ------------------------------------------------------
    def test_jalali_round_trip(self):
        self.assertEqual(gregorian_to_jalali(2026, 10, 13), (1405, 7, 21))
        self.assertEqual(gregorian_to_jalali(2025, 3, 21), (1404, 1, 1))
        for d in [dt.date(2024, 3, 20), dt.date(2026, 3, 20), dt.date(2030, 12, 31)]:
            jy, jm, jd = gregorian_to_jalali(d.year, d.month, d.day)
            self.assertEqual(jalali_to_gregorian(jy, jm, jd), (d.year, d.month, d.day))
        self.assertEqual(format_date(dt.date(2026, 10, 13), "fa"), "سه‌شنبه ۲۱ مهر ۱۴۰۵")

    # -- public pages --------------------------------------------------
    def test_pages_render_in_three_languages(self):
        for lang in ["fa", "ar", "en"]:
            for url in ["/", "/treatments/", "/treatments/rhinoplasty/", "/treatments/results/", "/book/"]:
                resp = self.client.get(f"/{lang}{url}")
                self.assertEqual(resp.status_code, 200, f"/{lang}{url}")
        fa = self.client.get("/fa/").content.decode()
        self.assertIn('dir="rtl"', fa)
        self.assertIn("نتیجه‌ای طبیعی", fa)
        en = self.client.get("/en/").content.decode()
        self.assertIn('dir="ltr"', en)
        self.assertIn("Natural results", en)
        ar = self.client.get("/ar/treatments/rhinoplasty/").content.decode()
        self.assertIn("تجميل الأنف", ar)
        self.assertIn('hreflang="en"', ar)
        self.assertIn('"@type": "MedicalProcedure"', ar)

    def test_seo_files(self):
        self.assertContains(self.client.get("/robots.txt"), "Sitemap:")
        sitemap = self.client.get("/sitemap.xml").content.decode()
        self.assertIn("/ar/treatments/rhinoplasty/", sitemap)
        self.assertIn('hreflang="x-default"', sitemap)

    # -- booking -------------------------------------------------------
    def _book(self, **extra):
        data = {
            "procedure": self.rhino.pk, "full_name": "سارا محمدی", "phone": "۰۹۱۲ ۳۴۵ ۶۷۸۹",
            "preferred_date": next_open_day().isoformat(), "time_slot": "10:30",
            "source_url": "/fa/treatments/rhinoplasty/", "source_title": "جراحی بینی — دورهٔ نقاهت",
        }
        data.update(extra)
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(reverse("bookings:submit"), data, HTTP_X_REQUESTED_WITH="fetch")

    @mock.patch("requests.Session.post", return_value=FakeResponse())
    def test_booking_creates_appointment_and_notifies_telegram(self, post):
        resp = self._book()
        self.assertEqual(resp.status_code, 200, resp.content)
        body = resp.json()
        self.assertTrue(body["ok"])
        a = Appointment.objects.get(code=body["code"])
        self.assertEqual(a.phone, "09123456789")  # Persian digits normalised
        self.assertEqual(a.source_title, "جراحی بینی — دورهٔ نقاهت")
        url, kwargs = post.call_args[0][0], post.call_args[1]
        self.assertIn("/bot123:ABC/sendMessage", url)
        self.assertIn("درخواست نوبت جدید", kwargs["json"]["text"])
        self.assertEqual(kwargs["json"]["reply_markup"]["inline_keyboard"][0][0]["callback_data"], f"ap:{a.pk}:confirmed")
        self.assertTrue(DeliveryLog.objects.filter(channel=self.channel, ok=True).exists())

    @mock.patch("requests.Session.post", return_value=FakeResponse())
    def test_slot_capacity_and_validation(self, post):
        self.assertEqual(self._book().status_code, 200)
        taken = self._book(full_name="علی رضایی", phone="09350000000")
        self.assertEqual(taken.status_code, 400)
        self.assertIn("time_slot", taken.json()["errors"])
        bad = self._book(phone="123", time_slot="11:00")
        self.assertIn("phone", bad.json()["errors"])
        friday = timezone.localdate() + dt.timedelta(days=(4 - timezone.localdate().weekday()) % 7 or 7)
        closed = self._book(preferred_date=friday.isoformat(), time_slot="11:00")
        self.assertIn("preferred_date", closed.json()["errors"])
        spam = self._book(website="http://spam", time_slot="11:30")
        self.assertEqual(spam.status_code, 400)

    def test_slots_endpoint(self):
        day = next_open_day()
        data = self.client.get(reverse("bookings:slots"), {"date": day.isoformat()}).json()
        self.assertTrue(data["ok"])
        self.assertEqual(len(data["slots"]), len(SiteSettings.load().slot_list))

    # -- chat ------------------------------------------------------------
    @mock.patch("requests.Session.post", return_value=FakeResponse())
    def test_chat_carries_page_context_to_staff(self, post):
        ctx = {"title": "جراحی بینی", "url": "/fa/treatments/rhinoplasty/", "section": "دورهٔ نقاهت", "evil": "x" * 999}
        with self.captureOnCommitCallbacks(execute=True):
            resp = self.client.post(reverse("chat:start"), json.dumps({
                "recipient": "doctor", "name": "سارا", "phone": "", "body": "آتل چند روز می‌ماند؟", "context": ctx,
            }), content_type="application/json")
        self.assertEqual(resp.status_code, 200, resp.content)
        thread = Thread.objects.get()
        self.assertEqual(thread.recipient, "doctor")
        self.assertEqual(thread.page_context["section"], "دورهٔ نقاهت")
        self.assertNotIn("evil", thread.page_context)
        sent = post.call_args[1]["json"]["text"]
        self.assertIn("#C%d" % thread.pk, sent)
        self.assertIn("دورهٔ نقاهت", sent)

        # Staff reply in the panel reaches the visitor.
        doctor = User.objects.get(username="doctor")
        staff = self.client_class()
        staff.force_login(doctor)
        page = staff.get(reverse("panel:chat_detail", args=[thread.pk]))
        self.assertContains(page, "دورهٔ نقاهت")
        staff.post(reverse("panel:chat_api", args=[thread.pk]), {"body": "یک هفته."})
        state = self.client.get(reverse("chat:state")).json()
        self.assertEqual([m["body"] for m in state["messages"]], ["آتل چند روز می‌ماند؟", "یک هفته."])
        self.assertEqual(state["unread"], 1)

    # -- Telegram webhook ------------------------------------------------
    def _hook(self, update, secret=None):
        url = reverse("notifications:bot_webhook", args=[self.channel.pk, secret or self.channel.webhook_secret])
        return self.client.post(url, json.dumps(update), content_type="application/json")

    @mock.patch("requests.Session.post", return_value=FakeResponse())
    def test_telegram_reply_and_confirm_button(self, post):
        thread = Thread.objects.create(visitor_name="سارا", recipient="secretary")
        self.assertEqual(self._hook({}, secret="wrong").status_code, 403)

        reply = {"message": {"message_id": 9, "chat": {"id": -1001}, "from": {"first_name": "منشی"},
                             "text": "فردا ساعت ۱۰ تشریف بیاورید",
                             "reply_to_message": {"text": f"پیام تازه {thread.tag}\n..."}}}
        self.assertEqual(self._hook(reply).status_code, 200)
        msg = Message.objects.get(thread=thread)
        self.assertEqual((msg.sender, msg.via, msg.staff_name), ("staff", "telegram", "منشی"))

        # Messages from other chats are ignored.
        reply["message"]["chat"]["id"] = 555
        self._hook(reply)
        self.assertEqual(Message.objects.filter(thread=thread).count(), 1)

        a = Appointment.objects.create(full_name="x", phone="0912", procedure=self.rhino,
                                       preferred_date=next_open_day(), time_slot="10:00")
        cb = {"callback_query": {"id": "q1", "data": f"ap:{a.pk}:confirmed", "from": {"first_name": "دکتر"},
                                 "message": {"message_id": 3, "chat": {"id": -1001}}}}
        self._hook(cb)
        a.refresh_from_db()
        self.assertEqual(a.status, "confirmed")
        self.assertIn("دکتر", a.staff_note)

    # -- panel ---------------------------------------------------------
    def test_panel_access_rules(self):
        self.assertRedirects(self.client.get("/panel/"), "/panel/login/?next=/panel/", fetch_redirect_response=False)
        secretary = User.objects.get(username="secretary")
        self.client.force_login(secretary)
        for name in ["panel:dashboard", "panel:appointments", "panel:chats"]:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)
        self.assertEqual(self.client.get(reverse("panel:settings")).status_code, 403)
        outsider = User.objects.create_user("guest", password="x")
        self.client.force_login(outsider)
        self.assertEqual(self.client.get(reverse("panel:dashboard")).status_code, 403)

    @mock.patch("requests.Session.post", return_value=FakeResponse())
    def test_panel_status_change_and_csv(self, post):
        a = Appointment.objects.create(full_name="مریم", phone="0912", procedure=self.rhino,
                                       preferred_date=next_open_day(), time_slot="10:00")
        self.client.force_login(User.objects.get(username="doctor"))
        with self.captureOnCommitCallbacks(execute=True):
            r = self.client.post(reverse("panel:appointment_status", args=[a.pk]), {"status": "confirmed"})
        self.assertEqual(r.json()["status"], "confirmed")
        self.assertIn("وضعیت نوبت تغییر کرد", post.call_args[1]["json"]["text"])
        csv = self.client.get(reverse("panel:appointments_csv")).content.decode("utf-8-sig")
        self.assertIn("مریم", csv)
        self.assertEqual(self.client.get(reverse("panel:settings")).status_code, 200)
        self.assertEqual(self.client.get(reverse("panel:channel_edit", args=[self.channel.pk])).status_code, 200)
