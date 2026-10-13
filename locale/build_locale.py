"""Fill locale/{fa,ar}/LC_MESSAGES/django.po from translations.py and compile .mo files.

    python manage.py makemessages -l fa -l ar --ignore=staticfiles --ignore=media
    python locale/build_locale.py

Works without GNU gettext (uses polib); install it with `pip install polib`.
"""
import sys
from pathlib import Path

import polib

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from translations import PLURALS, T  # noqa: E402

PLURAL_FORMS = {
    "fa": "nplurals=2; plural=(n > 1);",
    "ar": "nplurals=6; plural=n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 && n%100<=99 ? 4 : 5;",
}
INDEX = {"fa": 0, "ar": 1}


def build(lang: str) -> int:
    path = HERE / lang / "LC_MESSAGES" / "django.po"
    po = polib.pofile(str(path))
    po.metadata["Plural-Forms"] = PLURAL_FORMS[lang]
    po.metadata["Language"] = lang
    po.metadata["Content-Type"] = "text/plain; charset=UTF-8"
    missing = []
    for entry in po:
        entry.flags = [f for f in entry.flags if f != "fuzzy"]
        if entry.msgid_plural:
            text = PLURALS.get(entry.msgid, T.get(entry.msgid, (None, None)))[INDEX[lang]]
            if text is None:
                missing.append(entry.msgid)
                continue
            n = 2 if lang == "fa" else 6
            entry.msgstr_plural = {i: text for i in range(n)}
        else:
            pair = T.get(entry.msgid)
            if not pair:
                missing.append(entry.msgid)
                continue
            entry.msgstr = pair[INDEX[lang]]
    po.save(str(path))
    po.save_as_mofile(str(path.with_suffix(".mo")))
    for m in missing:
        print(f"[{lang}] missing: {m}")
    return len(missing)


if __name__ == "__main__":
    total = sum(build(lang) for lang in ("fa", "ar"))
    print("done" if not total else f"done with {total} missing")
