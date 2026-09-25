"""Examination detail, update, delete and cross-user isolation (Slice 8)."""

from datetime import date

import pytest

from examinations.models import ExaminationRecord, RecurrenceRule, Reminder

pytestmark = pytest.mark.django_db

LIST_URL = "/api/v1/examinations/"
NOT_FOUND = {"detail": "Not found."}


def detail_url(record_or_id):
    record_id = getattr(record_or_id, "pk", record_or_id)
    return f"/api/v1/examinations/{record_id}/"


def make_record(user, **fields):
    defaults = {
        "title": "Annual dental checkup",
        "status": "planned",
        "scheduled_date": date(2026, 9, 15),
    }
    return ExaminationRecord.objects.create(user=user, **{**defaults, **fields})


@pytest.fixture
def other_user(make_user):
    return make_user(email="someone-else@example.com")


@pytest.fixture
def other_client(other_user, client_for):
    return client_for(other_user)


def test_tc_fr_013_01_optional_metadata_fields_are_saved_and_retrieved(owner_client):
    """TC-FR-013-01 — Optional metadata fields are saved and retrieved."""
    created = owner_client.post(
        LIST_URL,
        {
            "title": "Annual dental checkup",
            "status": "planned",
            "scheduled_date": "2026-09-15",
            "medical_specialty": "Dentistry",
            "location": "Central Dental Clinic",
            "notes": "Routine appointment",
        },
        format="json",
    )
    assert created.status_code == 201

    retrieved = owner_client.get(detail_url(created.json()["id"])).json()

    assert retrieved["medical_specialty"] == "Dentistry"
    assert retrieved["location"] == "Central Dental Clinic"
    assert retrieved["notes"] == "Routine appointment"


def test_tc_fr_013_02_optional_metadata_fields_can_be_cleared(owner, owner_client):
    """TC-FR-013-02 — Optional metadata fields can be cleared."""
    record = make_record(
        owner, medical_specialty="Dentistry", location="Central Dental Clinic", notes="Routine"
    )

    response = owner_client.patch(
        detail_url(record),
        {"medical_specialty": None, "location": None, "notes": None},
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert (body["medical_specialty"], body["location"], body["notes"]) == (None, None, None)
    retrieved = owner_client.get(detail_url(record)).json()
    assert (retrieved["medical_specialty"], retrieved["location"], retrieved["notes"]) == (
        None,
        None,
        None,
    )


def test_tc_fr_016_01_a_draft_becomes_planned_when_a_scheduled_date_is_added(owner, owner_client):
    """TC-FR-016-01 — A draft becomes planned when a scheduled date is added."""
    draft = make_record(owner, title="Eye exam", status="draft", scheduled_date=None)

    response = owner_client.patch(
        detail_url(draft), {"status": "planned", "scheduled_date": "2026-09-10"}, format="json"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "planned"
    assert response.json()["scheduled_date"] == "2026-09-10"
    assert response.json()["category"] is None and response.json()["scheduled_time"] is None
    draft.refresh_from_db()
    assert (draft.status, draft.scheduled_date) == ("planned", date(2026, 9, 10))


def test_tc_fr_016_02_changing_a_draft_to_planned_without_a_scheduled_date_is_rejected(
    owner, owner_client
):
    """TC-FR-016-02 — Changing a draft to planned without a scheduled date is rejected."""
    draft = make_record(owner, title="Eye exam", status="draft", scheduled_date=None)

    response = owner_client.patch(detail_url(draft), {"status": "planned"}, format="json")

    assert response.status_code == 400
    assert response.json()["scheduled_date"]
    draft.refresh_from_db()
    assert draft.status == "draft"


def test_tc_fr_021_01_retrieving_an_owned_examination_returns_its_stored_fields(
    owner, owner_client
):
    """TC-FR-021-01 — Retrieving an owned examination returns its stored fields."""
    record = make_record(
        owner, medical_specialty="Dentistry", location="Central Dental Clinic", notes="Routine"
    )

    response = owner_client.get(detail_url(record))

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == record.pk
    assert body["user_id"] == owner.pk
    assert body["title"] == record.title
    assert body["status"] == record.status
    assert body["scheduled_date"] == record.scheduled_date.isoformat()
    assert body["scheduled_time"] is None
    assert body["completed_date"] is None
    assert body["category"] is None
    assert (body["medical_specialty"], body["location"], body["notes"]) == (
        "Dentistry",
        "Central Dental Clinic",
        "Routine",
    )
    assert body["source_occurrence"] is None
    assert set(body) == {
        "id",
        "user_id",
        "category",
        "title",
        "medical_specialty",
        "scheduled_date",
        "scheduled_time",
        "completed_date",
        "status",
        "location",
        "notes",
        "source_occurrence",
        "time_state",
        "created_at",
        "updated_at",
    }


def test_tc_fr_022_01_updating_an_owned_examination_persists_the_change(owner, owner_client):
    """TC-FR-022-01 — Updating an owned examination persists the change."""
    record = make_record(owner, location="Old clinic")

    response = owner_client.patch(detail_url(record), {"location": "New clinic"}, format="json")

    assert response.status_code == 200
    assert response.json()["location"] == "New clinic"
    assert owner_client.get(detail_url(record)).json()["location"] == "New clinic"


def test_tc_fr_023_01_deleting_an_owned_examination_removes_it_permanently(owner, owner_client):
    """TC-FR-023-01 — Deleting an owned examination removes it permanently."""
    record = make_record(owner)

    response = owner_client.delete(detail_url(record))

    assert response.status_code == 204
    assert response.content == b""
    follow_up = owner_client.get(detail_url(record))
    assert follow_up.status_code == 404
    assert not ExaminationRecord.objects.filter(pk=record.pk).exists()


def test_tc_fr_023_02_deleting_an_examination_cascades_to_its_reminder_and_recurrence_rule(
    owner, owner_client
):
    """TC-FR-023-02 — Deleting an examination cascades to its reminder and recurrence rule."""
    record = make_record(owner)
    Reminder.objects.create(examination=record, offset_days=7)
    RecurrenceRule.objects.create(examination=record, interval="yearly")

    assert owner_client.delete(detail_url(record)).status_code == 204

    assert not Reminder.objects.filter(examination_id=record.pk).exists()
    assert not RecurrenceRule.objects.filter(examination_id=record.pk).exists()
    for resource in ("reminder", "recurrence"):
        response = owner_client.get(f"{detail_url(record)}{resource}/")
        assert response.status_code == 404
        assert response.json() == NOT_FOUND


def test_tc_sec_001_01_unauthenticated_requests_to_the_examination_endpoint_are_rejected(
    api_client,
):
    """TC-SEC-001-01 — Unauthenticated requests to the examination endpoint are rejected."""
    response = api_client.get(LIST_URL)

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication credentials were not provided."}


def test_tc_sec_002_01_a_user_cannot_retrieve_another_users_examination(owner, other_client):
    """TC-SEC-002-01 — A user cannot retrieve another user's examination."""
    record = make_record(owner)

    response = other_client.get(detail_url(record))

    assert response.status_code == 404
    assert response.json() == NOT_FOUND


def test_tc_sec_002_02_a_user_cannot_update_another_users_examination(owner, other_client):
    """TC-SEC-002-02 — A user cannot update another user's examination."""
    record = make_record(owner, location="Original clinic")

    response = other_client.patch(
        detail_url(record), {"location": "Changed", "title": "Changed"}, format="json"
    )

    assert response.status_code == 404
    record.refresh_from_db()
    assert (record.location, record.title) == ("Original clinic", "Annual dental checkup")


def test_tc_sec_002_03_a_user_cannot_delete_another_users_examination(owner, other_client):
    """TC-SEC-002-03 — A user cannot delete another user's examination."""
    record = make_record(owner)

    response = other_client.delete(detail_url(record))

    assert response.status_code == 404
    assert ExaminationRecord.objects.filter(pk=record.pk).exists()


def test_tc_sec_006_01_missing_and_foreign_examinations_return_identical_not_found_responses(
    owner, other_client
):
    """TC-SEC-006-01 — A missing examination and another user's examination return identical not-found responses."""
    foreign = make_record(owner)
    missing_id = ExaminationRecord.objects.order_by("-pk").first().pk + 1000
    assert not ExaminationRecord.objects.filter(pk=missing_id).exists()

    for_missing = other_client.get(detail_url(missing_id))
    for_foreign = other_client.get(detail_url(foreign))

    assert for_missing.status_code == for_foreign.status_code == 404
    assert for_missing.content == for_foreign.content
    assert for_missing.json() == for_foreign.json() == NOT_FOUND
    assert for_missing["Content-Type"] == for_foreign["Content-Type"]
