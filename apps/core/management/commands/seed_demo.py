"""Load demo content (treatments, before/after cases, FAQs, sample stories) and staff accounts.

    python manage.py seed_demo              # (re)load demo content + demo users — overwrites edited demo rows
    python manage.py seed_demo --if-empty   # only on an empty database (used by the run scripts)
    python manage.py seed_demo --reset      # wipe treatments/cases/FAQs/stories first

Everything is editable afterwards in /admin/. Replace the sample doctor,
stories and illustrations with real, consented material before launch.
"""
import shutil
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.models import SiteSettings, Testimonial
from apps.procedures.models import FAQ, Category, Procedure, ProcedureSection, ResultCase

from . import seed_content as C

LANGS = ("fa", "ar", "en")
SECTION_ORDER = [key for key, _ in ProcedureSection.KEY_CHOICES]


def tri(prefix, values):
    return {f"{prefix}_{code}": value for code, value in zip(LANGS, values)}


class Command(BaseCommand):
    help = "Load trilingual demo content and demo staff accounts."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete existing treatments, cases, FAQs and stories first.")
        parser.add_argument("--no-users", action="store_true", help="Do not create demo staff accounts.")
        parser.add_argument("--if-empty", action="store_true",
                            help="Only load content when there are no treatments yet (safe to run on every start).")

    @transaction.atomic
    def handle(self, *args, **opts):
        if opts["if_empty"] and Procedure.objects.exists():
            if not opts["no_users"]:
                self._users()
            self.stdout.write("Content already present — leaving your edits untouched.")
            return
        if opts["reset"]:
            ResultCase.objects.all().delete()
            FAQ.objects.all().delete()
            Testimonial.objects.all().delete()
            Procedure.objects.all().delete()
            Category.objects.all().delete()

        site = SiteSettings.load()
        for field, values in C.SITE.items():
            for code, value in zip(LANGS, values):
                setattr(site, f"{field}_{code}", value)
        site.phone = site.phone or "071-36000000"
        site.whatsapp = site.whatsapp or "989170000000"
        site.instagram = site.instagram or "rokhsar.clinic"
        site.telegram = site.telegram or "rokhsar_clinic"
        site.license_number = site.license_number or "123456"
        site.save()

        cats = {}
        for order, (slug, icon, names) in enumerate(C.CATEGORIES):
            cats[slug], _ = Category.objects.update_or_create(slug=slug, defaults={"icon": icon, "order": order, **tri("name", names)})

        procs = {}
        for order, data in enumerate(C.PROCEDURES):
            defaults = {
                "category": cats[data["category"]], "icon": data["icon"], "is_surgical": data["surgical"], "order": order,
                **tri("title", data["title"]), **tri("summary", data["summary"]), **tri("intro", data["intro"]),
                **tri("duration", data["duration"]), **tri("anesthesia", data["anesthesia"]),
                **tri("recovery", data["recovery"]), **tri("longevity", data["longevity"]),
                **tri("meta_description", data["meta"]),
            }
            proc, _ = Procedure.objects.update_or_create(slug=data["slug"], defaults=defaults)
            procs[data["slug"]] = proc
            for key, body in data["sections"].items():
                ProcedureSection.objects.update_or_create(
                    procedure=proc, key=key, defaults={"order": SECTION_ORDER.index(key), **tri("body", body)})
            faqs = data["faqs"]
            for i in range(0, len(faqs), 2):
                FAQ.objects.update_or_create(procedure=proc, question_fa=faqs[i][0],
                                             defaults={"order": i, **tri("question", faqs[i]), **tri("answer", faqs[i + 1])})

        for order, (q, a) in enumerate(C.GENERAL_FAQS):
            FAQ.objects.update_or_create(procedure=None, question_fa=q[0],
                                         defaults={"order": order, **tri("question", q), **tri("answer", a)})

        self._copy_case_images()
        for order, (img, proc_slug, title, caption, months, hero) in enumerate(C.CASES):
            ResultCase.objects.update_or_create(
                procedure=procs[proc_slug], title_en=title[2],
                defaults={
                    **tri("title", title), **tri("caption", caption), "months_after": months,
                    "is_hero": hero, "order": order, "patient_consent": False,
                    "before_image": f"cases/{img}-before.webp", "after_image": f"cases/{img}-after.webp",
                },
            )

        for order, (name, proc_slug, text, months) in enumerate(C.TESTIMONIALS):
            Testimonial.objects.update_or_create(
                name=name, defaults={"procedure": procs.get(proc_slug), "months_after": months, "order": order, **tri("text", text)})

        if not opts["no_users"]:
            self._users()
        self.stdout.write(self.style.SUCCESS("Demo content loaded."))
        self.stdout.write(self.style.WARNING(
            "Remember: the doctor profile, stories and before/after illustrations are SAMPLES. "
            "Replace them with real, consented material in /admin/ before going live."))

    def _copy_case_images(self):
        src = Path(settings.BASE_DIR) / "static" / "img" / "cases"
        dst = Path(settings.MEDIA_ROOT) / "cases"
        dst.mkdir(parents=True, exist_ok=True)
        for f in src.glob("*.webp"):
            target = dst / f.name
            if not target.exists():
                shutil.copy(f, target)

    def _users(self):
        doctor_group, _ = Group.objects.get_or_create(name="doctor")
        secretary_group, _ = Group.objects.get_or_create(name="secretary")
        # The doctor may edit site content in /admin/; the secretary works in the panel only.
        content_perms = Permission.objects.filter(content_type__app_label__in=["core", "procedures"])
        doctor_group.permissions.set(content_perms)
        accounts = [
            ("admin", "admin12345", True, True, None, "مدیر", "سایت"),
            ("doctor", "doctor12345", False, True, doctor_group, "افسون", "فاضل‌زاده"),
            ("secretary", "secretary12345", False, False, secretary_group, "سارا", "منشی"),
        ]
        for username, password, superuser, staff, group, first, last in accounts:
            user, created = User.objects.get_or_create(username=username, defaults={"first_name": first, "last_name": last})
            if created:
                user.set_password(password)
                user.is_staff = staff
                user.is_superuser = superuser
                user.save()
                self.stdout.write(f"  user {username} / {password}")
            elif username == "doctor" and (user.first_name, user.last_name) != (first, last):
                user.first_name, user.last_name = first, last  # keep the demo doctor's name current
                user.save(update_fields=["first_name", "last_name"])
            if group:
                user.groups.add(group)
