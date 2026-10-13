from django import template
from django.conf import settings
from django.urls import translate_url
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe

from apps.core.i18n import current_lang
from apps.core.jalali import format_date, localize_digits

register = template.Library()


@register.filter
def tr(obj, field):
    """{{ procedure|tr:"title" }} → value in the active language."""
    if obj is None:
        return ""
    return obj.tr(field)


@register.filter
def ldigits(value):
    """Show digits in the script of the active language (۱۲۳ / ١٢٣ / 123)."""
    return localize_digits(value, current_lang())


@register.filter
def jdate(value, style="long"):
    """Locale-aware date: Jalali for Persian, Gregorian for Arabic/English."""
    return format_date(value, current_lang(), style)


@register.filter
def rich(text):
    """Turn plain text into paragraphs and bullet lists.

    Blank line → new paragraph; lines starting with "- " → <ul>.
    Everything is escaped first, so admins cannot inject HTML.
    """
    if not text:
        return ""
    html = []
    for block in str(text).replace("\r\n", "\n").split("\n\n"):
        lines = [ln.strip() for ln in block.strip().split("\n") if ln.strip()]
        if not lines:
            continue
        if all(ln.startswith("- ") for ln in lines):
            items = "".join(f"<li>{conditional_escape(ln[2:])}</li>" for ln in lines)
            html.append(f'<ul class="ticks">{items}</ul>')
        else:
            html.append(f"<p>{'<br>'.join(conditional_escape(ln) for ln in lines)}</p>")
    return mark_safe("".join(html))


@register.simple_tag
def icon(name, cls="", label=""):
    """Inline SVG icon from the sprite in base.html."""
    aria = format_html('role="img" aria-label="{}"', label) if label else mark_safe('aria-hidden="true"')
    return format_html('<svg class="ic {}" {}><use href="#i-{}"></use></svg>', cls, aria, name)


@register.simple_tag(takes_context=True)
def lang_url(context, code):
    request = context.get("request")
    if not request:
        return f"/{code}/"
    return translate_url(request.get_full_path(), code)


@register.simple_tag(takes_context=True)
def absolute_url(context, path=""):
    request = context.get("request")
    if request is not None:
        return request.build_absolute_uri(path or request.path)
    return settings.SITE_BASE_URL.rstrip("/") + (path or "/")


@register.filter
def get_item(mapping, key):
    try:
        return mapping.get(key)
    except AttributeError:
        return None
