"""Structured data (schema.org JSON-LD) builders."""
import json

from django.utils.safestring import mark_safe


def to_jsonld(*objects) -> str:
    data = objects[0] if len(objects) == 1 else list(objects)
    text = json.dumps(data, ensure_ascii=False)
    # Make the JSON safe inside <script>: no tag can be closed from data.
    text = text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return mark_safe(text)


def clinic_schema(site, request) -> dict:
    data = {
        "@context": "https://schema.org",
        "@type": "MedicalClinic",
        "name": site.tr("clinic_name"),
        "description": site.tr("tagline"),
        "url": request.build_absolute_uri("/"),
        "telephone": site.phone,
        "address": {"@type": "PostalAddress", "streetAddress": site.tr("address")},
        "medicalSpecialty": "PlasticSurgery",
        "openingHours": site.tr("working_hours"),
    }
    if site.tr("doctor_name"):
        data["employee"] = {
            "@type": "Physician",
            "name": site.tr("doctor_name"),
            "medicalSpecialty": "PlasticSurgery",
            "description": site.tr("doctor_title"),
        }
    return data


def procedure_schema(procedure, request) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "MedicalProcedure",
        "name": procedure.tr("title"),
        "description": procedure.tr("summary"),
        "url": request.build_absolute_uri(procedure.get_absolute_url()),
        "procedureType": "https://schema.org/SurgicalProcedure" if procedure.is_surgical else "https://schema.org/NoninvasiveProcedure",
        "howPerformed": procedure.tr("anesthesia"),
    }


def faq_schema(faqs) -> dict | None:
    faqs = list(faqs)
    if not faqs:
        return None
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f.tr("question"),
             "acceptedAnswer": {"@type": "Answer", "text": f.tr("answer")}}
            for f in faqs
        ],
    }


def breadcrumb_schema(items, request) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": name, "item": request.build_absolute_uri(url)}
            for i, (name, url) in enumerate(items, start=1)
        ],
    }
