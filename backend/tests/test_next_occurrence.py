"""Next-occurrence creation (Slice 14)."""

from datetime import date, time

import pytest

from examinations.models import (
    ExaminationCategory,
    ExaminationRecord,
    RecurrenceRule,
    Reminder,
)

pytestmark = pytest.mark.django_db


def next_occurrence_url(record):
    return f"/api/v1/examinations/{record.pk}/next-occurrence/"


def recurring_source(user, status="planned", interval="yearly", **fields):
    defaults = {"scheduled_date": date(2026, 3, 15)}
    if status == "completed":
        defaults["completed_date"] = date(2026, 3, 15)
    source = ExaminationRecord.objects.create(
        user=user, title="Annual checkup", status=status, **{**defaults, **fields}
    )
    RecurrenceRule.objects.create(examination=source, interval=interval)
    return source


def generated_from(source):
    return ExaminationRecord.objects.filter(source_occurrence=source)


def assert_created_from(client, source, expected_date):
    response = client.post(next_occurrence_url(source))
    assert response.status_code == 201, response.content
    assert response.json()["status"] == "planned"
    assert response.json()["scheduled_date"] == expected_date
    assert generated_from(source).count() == 1
    return response


def test_tc_fr_041_01_requesting_the_next_occurrence_creates_exactly_one_planned_examination(
    owner, owner_client
):
    """TC-FR-041-01 — Requesting the next occurrence creates exactly one new planned examination."""
    source = recurring_source(owner, interval="yearly")
    before = ExaminationRecord.objects.count()

    response = assert_created_from(owner_client, source, "2027-03-15")

    assert ExaminationRecord.objects.count() == before + 1
    created = ExaminationRecord.objects.get(pk=response.json()["id"])
    assert (created.status, created.scheduled_date) == ("planned", date(2027, 3, 15))


def test_tc_fr_041_02_next_occurrence_creation_is_accepted_from_a_completed_source(
    owner, owner_client
):
    """TC-FR-041-02 — Next-occurrence creation is accepted from a completed source examination."""
    assert_created_from(owner_client, recurring_source(owner, "completed"), "2027-03-15")


def test_tc_fr_041_03_next_occurrence_creation_is_accepted_from_a_cancelled_source(
    owner, owner_client
):
    """TC-FR-041-03 — Next-occurrence creation is accepted from a cancelled source examination."""
    assert_created_from(owner_client, recurring_source(owner, "cancelled"), "2027-03-15")


def test_tc_fr_041_04_next_occurrence_creation_is_accepted_from_a_missed_source(
    owner, owner_client
):
    """TC-FR-041-04 — Next-occurrence creation is accepted from a missed source examination."""
    assert_created_from(owner_client, recurring_source(owner, "missed"), "2027-03-15")


def test_tc_fr_041_05_next_occurrence_creation_is_rejected_for_a_draft_source(owner, owner_client):
    """TC-FR-041-05 — Next-occurrence creation is rejected for a draft source examination."""
    source = recurring_source(owner, "draft")
    before = ExaminationRecord.objects.count()

    response = owner_client.post(next_occurrence_url(source))

    assert response.status_code == 400
    assert response.json()["non_field_errors"]
    assert ExaminationRecord.objects.count() == before


def test_tc_fr_041_06_a_repeated_request_returns_the_existing_occurrence(owner, owner_client):
    """TC-FR-041-06 — A repeated next-occurrence request returns the existing occurrence instead of a duplicate."""
    source = recurring_source(owner, interval="monthly")
    first = owner_client.post(next_occurrence_url(source))
    assert first.status_code == 201
    rows_after_first = ExaminationRecord.objects.count()

    repeat = owner_client.post(next_occurrence_url(source))

    assert repeat.status_code == 200
    assert repeat.json() == first.json()
    assert ExaminationRecord.objects.count() == rows_after_first
    assert generated_from(source).count() == 1


def test_tc_fr_041_07_the_generated_occurrence_copies_the_documented_fields(owner, owner_client):
    """TC-FR-041-07 — The generated occurrence copies the documented fields and leaves the rest empty."""
    dental = ExaminationCategory.objects.get(slug="dental-appointment")
    source = recurring_source(
        owner,
        interval="six_months",
        category=dental,
        medical_specialty="Dentistry",
        scheduled_date=date(2026, 8, 31),
        scheduled_time=time(10, 30),
        location="Central Dental Clinic",
        notes="Bring the insurance card",
    )
    Reminder.objects.create(examination=source, offset_days=7)

    response = owner_client.post(next_occurrence_url(source))

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Annual checkup"
    assert body["category"]["id"] == dental.pk
    assert body["medical_specialty"] == "Dentistry"
    assert body["scheduled_time"] == "10:30:00"
    assert body["location"] == "Central Dental Clinic"
    assert body["status"] == "planned"
    assert body["scheduled_date"] == "2027-02-28"
    assert body["source_occurrence"] == source.pk
    assert body["notes"] is None
    assert body["completed_date"] is None
    generated = ExaminationRecord.objects.get(pk=body["id"])
    assert not Reminder.objects.filter(examination=generated).exists()
    assert not RecurrenceRule.objects.filter(examination=generated).exists()


def test_tc_fr_023_03_deleting_a_source_nulls_rather_than_deletes_a_generated_occurrence(
    owner, owner_client
):
    """TC-FR-023-03 — Deleting a source examination nulls, rather than deletes, a generated occurrence's source reference."""
    source = recurring_source(owner)
    generated_id = owner_client.post(next_occurrence_url(source)).json()["id"]

    assert owner_client.delete(f"/api/v1/examinations/{source.pk}/").status_code == 204

    response = owner_client.get(f"/api/v1/examinations/{generated_id}/")
    assert response.status_code == 200
    assert response.json()["source_occurrence"] is None
    assert response.json()["title"] == "Annual checkup"
