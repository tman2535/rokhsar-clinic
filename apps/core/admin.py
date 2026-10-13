from django.contrib import admin

from .models import SiteSettings, Testimonial


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "procedure", "rating", "is_published", "order")
    list_editable = ("is_published", "order")
    list_filter = ("is_published", "procedure")
