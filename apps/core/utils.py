import re

from django.core.cache import cache

from .jalali import to_latin_digits

PHONE_RE = re.compile(r"^\+?\d{8,15}$")


def client_ip(request) -> str | None:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def normalize_phone(raw: str) -> str:
    """Accept Persian/Arabic digits, spaces, dashes; return digits with optional leading +."""
    value = to_latin_digits(raw or "").strip()
    value = re.sub(r"[\s\-()]", "", value)
    if value.startswith("00"):
        value = "+" + value[2:]
    return value


def is_valid_phone(value: str) -> bool:
    return bool(PHONE_RE.match(value))


def rate_limited(key: str, limit: int, window: int) -> bool:
    """Simple fixed-window limiter. Returns True when the caller should be blocked."""
    cache_key = f"rl:{key}"
    added = cache.add(cache_key, 1, window)
    if added:
        return False
    try:
        count = cache.incr(cache_key)
    except ValueError:
        cache.set(cache_key, 1, window)
        return False
    return count > limit
