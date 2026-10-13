from django.contrib import admin

from .models import Channel, DeliveryLog


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "is_active", "target")
    list_filter = ("kind", "is_active")


@admin.register(DeliveryLog)
class DeliveryLogAdmin(admin.ModelAdmin):
    list_display = ("channel", "event", "ok", "created_at")
    list_filter = ("channel", "ok", "event")
