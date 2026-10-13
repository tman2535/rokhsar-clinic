from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("code", "full_name", "phone", "procedure", "preferred_date", "time_slot", "status", "created_at")
    list_filter = ("status", "procedure", "preferred_date")
    search_fields = ("code", "full_name", "phone")
    readonly_fields = ("code", "source_url", "source_title", "ip_address", "created_at", "updated_at")
