"""Register, inspect or remove the Telegram/Bale webhook for a notification channel.

    python manage.py bot_webhook            # list bot channels and their webhook URLs
    python manage.py bot_webhook 1 set      # register webhook for channel 1 (needs https SITE_BASE_URL)
    python manage.py bot_webhook 1 info     # show what Telegram knows about it
    python manage.py bot_webhook 1 delete   # remove it
"""
from django.core.management.base import BaseCommand, CommandError

from apps.notifications.backends import bot_call
from apps.notifications.models import Channel
from apps.notifications.services import absolute


class Command(BaseCommand):
    help = "Manage the Telegram/Bale bot webhook of a notification channel."

    def add_arguments(self, parser):
        parser.add_argument("channel", nargs="?", type=int)
        parser.add_argument("action", nargs="?", choices=["set", "info", "delete"], default="info")

    def handle(self, *args, channel=None, action="info", **opts):
        bots = Channel.objects.filter(kind__in=["telegram", "bale"])
        if channel is None:
            for c in bots:
                self.stdout.write(f"{c.pk}: {c} → {absolute(c.webhook_path())}")
            if not bots:
                self.stdout.write("No Telegram/Bale channels yet. Add one in /panel/settings/.")
            return
        try:
            c = bots.get(pk=channel)
        except Channel.DoesNotExist as exc:
            raise CommandError(f"No Telegram/Bale channel with id {channel}") from exc
        if action == "set":
            url = absolute(c.webhook_path())
            if not url.startswith("https://"):
                raise CommandError("SITE_BASE_URL must be a public https address.")
            ok, data = bot_call(c, "setWebhook", {"url": url, "allowed_updates": ["message", "callback_query"]})
        elif action == "delete":
            ok, data = bot_call(c, "deleteWebhook", {})
        else:
            ok, data = bot_call(c, "getWebhookInfo", {})
        self.stdout.write((self.style.SUCCESS if ok else self.style.ERROR)(str(data)))
