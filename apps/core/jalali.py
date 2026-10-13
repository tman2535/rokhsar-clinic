"""Gregorian ⇄ Jalali (Solar Hijri) conversion and locale-aware date formatting.

Algorithm: the widely used arithmetic conversion (same as jalaali-js),
valid for the full range a clinic will ever need.
"""
from __future__ import annotations

import datetime as dt

FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
AR_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
TO_LATIN = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

FA_MONTHS = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
             "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
FA_WEEKDAYS = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه", "یکشنبه"]
AR_MONTHS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
             "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
AR_WEEKDAYS = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]


def gregorian_to_jalali(gy: int, gm: int, gd: int) -> tuple[int, int, int]:
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy + 1 if gm > 2 else gy
    days = (355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100)
            + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1])
    jy = -1595 + (33 * (days // 12053))
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    return jy, jm, jd


def jalali_to_gregorian(jy: int, jm: int, jd: int) -> tuple[int, int, int]:
    jy += 1595
    days = -355668 + (365 * jy) + ((jy // 33) * 8) + (((jy % 33) + 3) // 4) + jd
    days += (jm - 1) * 31 if jm < 7 else ((jm - 7) * 30) + 186
    gy = 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        days -= 1
        gy += 100 * (days // 36524)
        days %= 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += (days - 1) // 365
        days = (days - 1) % 365
    gd = days + 1
    leap = (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)
    month_days = [0, 31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 0
    for gm in range(13):
        v = month_days[gm]
        if gd <= v:
            break
        gd -= v
    return gy, gm, gd


def localize_digits(value, lang: str) -> str:
    text = str(value)
    if lang == "fa":
        return text.translate(FA_DIGITS)
    if lang == "ar":
        return text.translate(AR_DIGITS)
    return text


def to_latin_digits(value: str) -> str:
    return (value or "").translate(TO_LATIN)


def format_date(value: dt.date | dt.datetime | None, lang: str, style: str = "long") -> str:
    """Format a date for display. Persian uses the Jalali calendar."""
    if value is None:
        return ""
    if isinstance(value, dt.datetime):
        value = value.date()
    if lang == "fa":
        jy, jm, jd = gregorian_to_jalali(value.year, value.month, value.day)
        if style == "short":
            text = f"{jy}/{jm:02d}/{jd:02d}"
        elif style == "weekday":
            text = f"{FA_WEEKDAYS[value.weekday()]} {jd} {FA_MONTHS[jm - 1]}"
        else:
            text = f"{FA_WEEKDAYS[value.weekday()]} {jd} {FA_MONTHS[jm - 1]} {jy}"
        return localize_digits(text, "fa")
    if lang == "ar":
        if style == "short":
            text = f"{value.year}/{value.month:02d}/{value.day:02d}"
        elif style == "weekday":
            text = f"{AR_WEEKDAYS[value.weekday()]} {value.day} {AR_MONTHS[value.month - 1]}"
        else:
            text = f"{AR_WEEKDAYS[value.weekday()]} {value.day} {AR_MONTHS[value.month - 1]} {value.year}"
        return localize_digits(text, "ar")
    if style == "short":
        return value.strftime("%Y-%m-%d")
    if style == "weekday":
        return value.strftime("%a %d %b")
    return value.strftime("%A, %d %B %Y")
