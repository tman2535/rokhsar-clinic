from django.contrib import admin
from django.utils.html import format_html

from .models import FAQ, Category, Procedure, ProcedureSection, ResultCase


class SectionInline(admin.StackedInline):
    model = ProcedureSection
    extra = 0


class FAQInline(admin.StackedInline):
    model = FAQ
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name_fa", "name_en", "slug", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name_en",)}


@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    list_display = ("title_fa", "title_en", "category", "is_surgical", "is_featured", "is_published", "order")
    list_editable = ("is_featured", "is_published", "order")
    list_filter = ("category", "is_surgical", "is_published")
    search_fields = ("title_fa", "title_en", "title_ar", "slug")
    prepopulated_fields = {"slug": ("title_en",)}
    inlines = [SectionInline, FAQInline]


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question_fa", "procedure", "order", "is_published")
    list_filter = ("procedure", "is_published")


@admin.register(ResultCase)
class ResultCaseAdmin(admin.ModelAdmin):
    list_display = ("thumb", "__str__", "procedure", "months_after", "patient_consent", "is_hero", "is_published")
    list_editable = ("is_hero", "is_published")
    list_filter = ("procedure", "is_published", "patient_consent")

    @admin.display(description="")
    def thumb(self, obj):
        if obj.after_image:
            return format_html('<img src="{}" style="height:48px;border-radius:8px">', obj.after_image.url)
        return ""
