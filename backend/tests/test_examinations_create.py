"""Categories, examination creation and status-dependent validation (Slice 7)."""

from datetime import UTC, date, datetime, time

import pytest
from freezegun import freeze_time

from examinations.models import ExaminationCategory, ExaminationRecord
from examinations.serializers import ExaminationSerializer

pytestmark = pytest.mark.django_db

EXAMINATIONS_URL = "/api/v1/examinations/"
CATEGORIES_URL = "/api/v1/categories/"
REQUIRED_CATEGORIES = [
    "General medical appointment",
    "Dental appointment",
    "Specialist consultation",
    "Laboratory test",
    "Vaccination",
    "Preventive examination",
    "Follow-up",
    "Other",
]
# The user's local date is 2026-08-04 while the UTC date is still 2026-08-03.
AUCKLAND_MORNING_UTC = "2026-08-03T13:00:00+00:00"


def create(client, **data):
    return client.post(EXAMINATIONS_URL, data, format="json")


def assert_field_error(response, field):
    assert response.status_code == 400, response.content
    assert response.json()[field]


def dental():
    return ExaminationCategory.objects.get(slug="dental-appointment")


def test_tc_fr_010_01_draft_creation_preserves_title_and_supplied_optional_information(
    owner_client,
):
    """TC-FR-010-01 — Draft creation preserves title and supplied optional information."""
    response = create(
        owner_client, status="draft", title="Annual eye examination", scheduled_date="2026-09-10"
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "draft"
    assert body["title"] == "Annual eye examination"
    assert body["scheduled_date"] == "2026-09-10"
    assert body["category"] is None
    assert body["scheduled_time"] is None
    stored = ExaminationRecord.objects.get(pk=body["id"])
    assert (stored.status, stored.title, stored.scheduled_date) == (
        "draft",
        "Annual eye examination",
        date(2026, 9, 10),
    )


def test_tc_fr_011_01_minimal_planned_creation_succeeds_with_only_title_and_scheduled_date(
    owner_client,
):
    """TC-FR-011-01 — Minimal planned creation succeeds with only title and scheduled date."""
    response = create(
        owner_client, status="planned", title="Annual eye examination", scheduled_date="2026-09-10"
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "planned"
    assert (body["title"], body["scheduled_date"]) == ("Annual eye examination", "2026-09-10")
    assert body["category"] is None and body["scheduled_time"] is None
    stored = ExaminationRecord.objects.get(pk=body["id"])
    assert stored.status == "planned"
    assert stored.category is None and stored.scheduled_time is None


def assert_status_accepted(client, status, **fields):
    response = create(client, status=status, title=f"A {status} examination", **fields)
    assert response.status_code == 201, response.content
    assert response.json()["status"] == status
    assert ExaminationRecord.objects.get(pk=response.json()["id"]).status == status


def test_tc_fr_012_01_the_draft_status_value_is_accepted(owner_client):
    """TC-FR-012-01 — The draft status value is accepted."""
    assert_status_accepted(owner_client, "draft")


def test_tc_fr_012_02_the_planned_status_value_is_accepted(owner_client):
    """TC-FR-012-02 — The planned status value is accepted."""
    assert_status_accepted(owner_client, "planned", scheduled_date="2026-09-10")


def test_tc_fr_012_03_the_completed_status_value_is_accepted(owner_client):
    """TC-FR-012-03 — The completed status value is accepted."""
    with freeze_time("2026-08-04T12:00:00+00:00"):
        assert_status_accepted(owner_client, "completed", completed_date="2026-08-01")


def test_tc_fr_012_04_the_cancelled_status_value_is_accepted(owner_client):
    """TC-FR-012-04 — The cancelled status value is accepted."""
    assert_status_accepted(owner_client, "cancelled", scheduled_date="2026-09-10")


def test_tc_fr_012_05_the_missed_status_value_is_accepted(owner_client):
    """TC-FR-012-05 — The missed status value is accepted."""
    assert_status_accepted(owner_client, "missed", scheduled_date="2026-07-10")


def test_tc_fr_012_06_an_unsupported_status_value_is_rejected(owner_client):
    """TC-FR-012-06 — An unsupported status value is rejected."""
    response = create(owner_client, status="archived", title="Archived examination")

    assert_field_error(response, "status")
    assert ExaminationRecord.objects.count() == 0


def test_tc_fr_014_01_missing_title_is_rejected_for_any_status(owner_client):
    """TC-FR-014-01 — Missing title is rejected for any status."""
    response = create(owner_client, status="planned", scheduled_date="2026-09-10")

    assert_field_error(response, "title")
    assert ExaminationRecord.objects.count() == 0


def test_tc_fr_014_02_a_planned_examination_without_a_scheduled_date_is_rejected(owner_client):
    """TC-FR-014-02 — A planned examination without a scheduled date is rejected."""
    response = create(owner_client, status="planned", title="No date")

    assert_field_error(response, "scheduled_date")
    assert ExaminationRecord.objects.count() == 0


def test_tc_fr_014_03_a_cancelled_examination_without_a_scheduled_date_is_rejected(
    owner_client,
):
    """TC-FR-014-03 — A cancelled examination without a scheduled date is rejected."""
    response = create(owner_client, status="cancelled", title="No date")

    assert_field_error(response, "scheduled_date")
    assert ExaminationRecord.objects.count() == 0


def test_tc_fr_014_04_a_missed_examination_without_a_scheduled_date_is_rejected(owner_client):
    """TC-FR-014-04 — A missed examination without a scheduled date is rejected."""
    response = create(owner_client, status="missed", title="No date")

    assert_field_error(response, "scheduled_date")
    assert ExaminationRecord.objects.count() == 0


def test_tc_fr_014_05_a_completed_examination_without_a_completion_date_is_rejected(
    owner_client,
):
    """TC-FR-014-05 — A completed examination without a completion date is rejected."""
    response = create(owner_client, status="completed", title="No completion date")

    assert_field_error(response, "completed_date")
    assert ExaminationRecord.objects.count() == 0


def test_tc_fr_014_06_a_completion_date_equal_to_the_current_local_date_is_accepted(
    make_user, client_for
):
    """TC-FR-014-06 — A completion date equal to the current local date is accepted."""
    user = make_user(timezone="Pacific/Auckland")
    with freeze_time(AUCKLAND_MORNING_UTC):
        response = create(
            client_for(user), status="completed", title="Blood test", completed_date="2026-08-04"
        )

    assert response.status_code == 201, response.content
    assert ExaminationRecord.objects.get(pk=response.json()["id"]).completed_date == date(
        2026, 8, 4
    )


def test_tc_fr_014_07_a_completion_date_after_the_current_local_date_is_rejected(
    make_user, client_for
):
    """TC-FR-014-07 — A completion date after the current local date is rejected."""
    user = make_user(timezone="Pacific/Auckland")
    with freeze_time(AUCKLAND_MORNING_UTC):
        response = create(
            client_for(user), status="completed", title="Blood test", completed_date="2026-08-05"
        )

    assert_field_error(response, "completed_date")
    assert ExaminationRecord.objects.count() == 0


def test_tc_fr_015_01_a_nonexistent_category_is_rejected(owner_client):
    """TC-FR-015-01 — A nonexistent category is rejected."""
    assert not ExaminationCategory.objects.filter(pk=9999).exists()

    response = create(owner_client, status="draft", title="Checkup", category_id=9999)

    assert_field_error(response, "category_id")
    assert ExaminationRecord.objects.count() == 0


def test_tc_fr_015_02_an_unsupported_status_is_rejected_during_category_and_status_validation(
    owner_client,
):
    """TC-FR-015-02 — An unsupported status value is rejected during category and status validation."""
    response = create(owner_client, status="archived", title="Checkup", category_id=dental().pk)

    assert_field_error(response, "status")
    assert "category_id" not in response.json()
    assert ExaminationRecord.objects.count() == 0


def test_tc_fr_025_01_assigning_an_available_category_is_saved_and_returned(owner_client):
    """TC-FR-025-01 — Assigning an available category is saved and returned."""
    category = dental()

    response = create(
        owner_client,
        status="planned",
        title="Annual dental checkup",
        scheduled_date="2026-09-10",
        category_id=category.pk,
    )

    assert response.status_code == 201
    assert response.json()["category"] == {
        "id": category.pk,
        "name": "Dental appointment",
        "slug": "dental-appointment",
    }
    assert "category_id" not in response.json()
    assert ExaminationRecord.objects.get(pk=response.json()["id"]).category == category


def test_tc_fr_026_01_the_category_collection_contains_exactly_the_required_categories(
    owner_client,
):
    """TC-FR-026-01 — The category collection contains exactly the required system-defined categories."""
    response = owner_client.get(CATEGORIES_URL)

    assert response.status_code == 200
    names = [category["name"] for category in response.json()]
    assert sorted(names) == sorted(REQUIRED_CATEGORIES)
    assert len(names) == len(set(names)) == 8
    slugs = [category["slug"] for category in response.json()]
    assert len(slugs) == len(set(slugs))


def test_tc_prv_002_01_an_examination_can_be_created_without_clinical_or_identity_data(
    owner_client,
):
    """TC-PRV-002-01 — An examination can be created without clinical or identity data."""
    response = create(
        owner_client,
        category_id=dental().pk,
        title="Annual dental checkup",
        medical_specialty="Dentistry",
        scheduled_date="2026-09-15",
        scheduled_time="10:30:00",
        status="planned",
        location="Central Dental Clinic",
        notes="Routine appointment",
    )

    assert response.status_code == 201
    writable = {
        name for name, field in ExaminationSerializer().fields.items() if not field.read_only
    }
    clinical_or_identity = {"diagnosis", "prescription", "medical_file", "insurance", "national_id"}
    assert not writable & clinical_or_identity
    assert writable == {
        "category_id",
        "title",
        "medical_specialty",
        "scheduled_date",
        "scheduled_time",
        "completed_date",
        "status",
        "location",
        "notes",
    }


def test_tc_tech_002_01_a_date_only_examination_field_round_trips_correctly(owner):
    """TC-TECH-002-01 — A date-only examination field round-trips correctly."""
    record = ExaminationRecord.objects.create(
        user=owner, title="Date only", status="planned", scheduled_date=date(2026, 8, 15)
    )

    record.refresh_from_db()

    assert type(record.scheduled_date) is date
    assert record.scheduled_date == date(2026, 8, 15)
    assert record.scheduled_time is None


def test_tc_tech_002_02_an_optional_scheduled_time_is_stored_separately(owner):
    """TC-TECH-002-02 — An examination with an optional scheduled time stores date and time separately."""
    record = ExaminationRecord.objects.create(
        user=owner,
        title="Date and time",
        status="planned",
        scheduled_date=date(2026, 8, 15),
        scheduled_time=time(10, 30),
    )

    record.refresh_from_db()

    assert type(record.scheduled_date) is date
    assert type(record.scheduled_time) is time
    assert (record.scheduled_date, record.scheduled_time) == (date(2026, 8, 15), time(10, 30))
    assert record.scheduled_time.tzinfo is None


def test_tc_tech_002_03_a_timezone_aware_audit_timestamp_round_trips_as_an_instant(owner):
    """TC-TECH-002-03 — A timezone-aware audit timestamp round-trips as an instant."""
    instant = datetime(2026, 7, 21, 4, 10, tzinfo=UTC)
    with freeze_time(instant):
        record = ExaminationRecord.objects.create(user=owner, title="Instant", status="draft")

    owner.timezone = "Pacific/Auckland"
    owner.save(update_fields=["timezone"])
    record.refresh_from_db()

    assert isinstance(record.created_at, datetime)
    assert record.created_at.tzinfo is not None
    assert record.created_at == instant
    assert record.created_at.utcoffset().total_seconds() == 0
