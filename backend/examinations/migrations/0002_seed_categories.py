"""Seed the eight system-defined categories (FR-026, ADS-FR-026-01).

Idempotent: rows are matched on their stable slug, so running it again creates no
duplicates; unique constraints on name and slug back that up.
"""

from django.db import migrations

CATEGORIES = [
    ("general-medical-appointment", "General medical appointment"),
    ("dental-appointment", "Dental appointment"),
    ("specialist-consultation", "Specialist consultation"),
    ("laboratory-test", "Laboratory test"),
    ("vaccination", "Vaccination"),
    ("preventive-examination", "Preventive examination"),
    ("follow-up", "Follow-up"),
    ("other", "Other"),
]


def seed_categories(apps, schema_editor):
    ExaminationCategory = apps.get_model("examinations", "ExaminationCategory")
    for slug, name in CATEGORIES:
        ExaminationCategory.objects.update_or_create(slug=slug, defaults={"name": name})


class Migration(migrations.Migration):
    dependencies = [("examinations", "0001_categories")]

    operations = [migrations.RunPython(seed_categories, migrations.RunPython.noop)]
