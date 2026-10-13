from django.contrib import admin

from .models import Message, Thread


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("sender", "staff_name", "body", "page_context", "via", "created_at")


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ("id", "visitor_name", "visitor_phone", "recipient", "status", "last_message_at")
    list_filter = ("recipient", "status")
    inlines = [MessageInline]
