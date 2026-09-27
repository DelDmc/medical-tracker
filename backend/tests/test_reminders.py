"""Reminder configuration, the planned-only rule and due dates (Slice 11)."""

from datetime import date

import pytest

from examinations.models import ExaminationRecord, Reminder

pytestmark = pytest.mark.django_db


def reminder_url(examination):
    return f"/api/v1/examinations/{examination.pk}/reminder/"


def examination(user, status="planned", **fields):
    defaults = {"scheduled_date": date(2026, 8, 15)}
    if status == "completed":
        defaults["completed_date"] = date(2026, 8, 1)
    return ExaminationRecord.objects.create(
        user=user, title=f"A {status} examination", status=status, **{**defaults, **fields}
    )


def attach_reminder(record, *, offset_days=7, is_active=True):
    return Reminder.objects.create(examination=record, offset_days=offset_days, is_active=is_active)


def assert_business_rule_error(response):
    assert response.status_code == 400, response.content
    assert response.json()["non_field_errors"]


def stored(reminder):
    return Reminder.objects.get(pk=reminder.pk)


# ---- Status restrictions shared by the FR-017 and FR-035 cases -------------------


def assert_creation_rejected(client, record):
    response = client.post(reminder_url(record), {"offset_days": 7}, format="json")
    assert_business_rule_error(response)
    assert not Reminder.objects.filter(examination=record).exists()


def assert_offset_update_rejected(client, record):
    reminder = attach_reminder(record, offset_days=7, is_active=False)
    response = client.patch(reminder_url(record), {"offset_days": 3}, format="json")
    assert_business_rule_error(response)
    assert stored(reminder).offset_days == 7


def assert_reactivation_rejected(client, record):
    reminder = attach_reminder(record, is_active=False)
    response = client.patch(reminder_url(record), {"is_active": True}, format="json")
    assert_business_rule_error(response)
    assert stored(reminder).is_active is False


def test_tc_fr_017_01_reminder_creation_is_rejected_for_a_draft_examination(owner, owner_client):
    """TC-FR-017-01 — Reminder creation is rejected for a draft examination."""
    assert_creation_rejected(owner_client, examination(owner, "draft"))


def test_tc_fr_017_02_reminder_offset_update_is_rejected_for_a_draft_examination(
    owner, owner_client
):
    """TC-FR-017-02 — Reminder offset update is rejected for a draft examination."""
    assert_offset_update_rejected(owner_client, examination(owner, "draft"))


def test_tc_fr_017_03_reminder_reactivation_is_rejected_for_a_draft_examination(
    owner, owner_client
):
    """TC-FR-017-03 — Reminder reactivation is rejected for a draft examination."""
    assert_reactivation_rejected(owner_client, examination(owner, "draft"))


def test_tc_fr_035_01_creating_a_reminder_on_a_planned_examination_succeeds(owner, owner_client):
    """TC-FR-035-01 — Creating a reminder on a planned examination succeeds."""
    record = examination(owner)

    response = owner_client.post(reminder_url(record), {"offset_days": 7}, format="json")

    assert response.status_code == 201
    assert response.json()["is_active"] is True
    assert response.json()["examination"] == record.pk
    assert response.json()["offset_days"] == 7
    assert Reminder.objects.filter(examination=record, is_active=True).count() == 1


def test_tc_fr_035_02_updating_the_offset_of_an_existing_reminder_succeeds(owner, owner_client):
    """TC-FR-035-02 — Updating the offset of an existing reminder succeeds."""
    record = examination(owner)
    reminder = attach_reminder(record, offset_days=7)

    response = owner_client.patch(reminder_url(record), {"offset_days": 3}, format="json")

    assert response.status_code == 200
    assert response.json()["offset_days"] == 3
    assert stored(reminder).offset_days == 3


def test_tc_fr_035_03_disabling_a_reminder_succeeds_while_the_examination_is_planned(
    owner, owner_client
):
    """TC-FR-035-03 — Disabling a reminder succeeds while the examination is planned."""
    record = examination(owner)
    reminder = attach_reminder(record)

    response = owner_client.patch(reminder_url(record), {"is_active": False}, format="json")

    assert response.status_code == 200
    assert response.json()["is_active"] is False
    assert stored(reminder).is_active is False


def test_tc_fr_035_04_disabling_a_reminder_succeeds_while_the_examination_is_completed(
    owner, owner_client
):
    """TC-FR-035-04 — Disabling a reminder succeeds while the examination is completed."""
    record = examination(owner, "completed")
    reminder = attach_reminder(record, is_active=True)

    response = owner_client.patch(reminder_url(record), {"is_active": False}, format="json")

    assert response.status_code == 200
    assert response.json()["is_active"] is False
    assert stored(reminder).is_active is False


@pytest.fixture
def planned(owner):
    return examination(owner)


def assert_offset_rejected(client, record, offset):
    response = client.post(reminder_url(record), {"offset_days": offset}, format="json")
    assert response.status_code == 400
    assert response.json()["offset_days"]
    assert not Reminder.objects.filter(examination=record).exists()


def test_tc_fr_035_05_a_zero_offset_is_rejected(planned, owner_client):
    """TC-FR-035-05 — A zero offset is rejected."""
    assert_offset_rejected(owner_client, planned, 0)


def test_tc_fr_035_06_a_negative_offset_is_rejected(planned, owner_client):
    """TC-FR-035-06 — A negative offset is rejected."""
    assert_offset_rejected(owner_client, planned, -3)


def test_tc_fr_035_07_a_non_whole_number_offset_is_rejected(planned, owner_client):
    """TC-FR-035-07 — A non-whole-number offset is rejected."""
    assert_offset_rejected(owner_client, planned, 2.5)
    assert_offset_rejected(owner_client, planned, "seven")


def test_tc_fr_035_08_reminder_creation_is_rejected_for_a_draft_examination(owner, owner_client):
    """TC-FR-035-08 — Reminder creation is rejected for a draft examination."""
    assert_creation_rejected(owner_client, examination(owner, "draft"))


def test_tc_fr_035_09_reminder_offset_update_is_rejected_for_a_draft_examination(
    owner, owner_client
):
    """TC-FR-035-09 — Reminder offset update is rejected for a draft examination."""
    assert_offset_update_rejected(owner_client, examination(owner, "draft"))


def test_tc_fr_035_10_reminder_reactivation_is_rejected_for_a_draft_examination(
    owner, owner_client
):
    """TC-FR-035-10 — Reminder reactivation is rejected for a draft examination."""
    assert_reactivation_rejected(owner_client, examination(owner, "draft"))


def test_tc_fr_035_11_reminder_creation_is_rejected_for_a_completed_examination(
    owner, owner_client
):
    """TC-FR-035-11 — Reminder creation is rejected for a completed examination."""
    assert_creation_rejected(owner_client, examination(owner, "completed"))


def test_tc_fr_035_12_reminder_offset_update_is_rejected_for_a_completed_examination(
    owner, owner_client
):
    """TC-FR-035-12 — Reminder offset update is rejected for a completed examination."""
    assert_offset_update_rejected(owner_client, examination(owner, "completed"))


def test_tc_fr_035_13_reminder_reactivation_is_rejected_for_a_completed_examination(
    owner, owner_client
):
    """TC-FR-035-13 — Reminder reactivation is rejected for a completed examination."""
    assert_reactivation_rejected(owner_client, examination(owner, "completed"))


def test_tc_fr_035_14_reminder_creation_is_rejected_for_a_cancelled_examination(
    owner, owner_client
):
    """TC-FR-035-14 — Reminder creation is rejected for a cancelled examination."""
    assert_creation_rejected(owner_client, examination(owner, "cancelled"))


def test_tc_fr_035_15_reminder_offset_update_is_rejected_for_a_cancelled_examination(
    owner, owner_client
):
    """TC-FR-035-15 — Reminder offset update is rejected for a cancelled examination."""
    assert_offset_update_rejected(owner_client, examination(owner, "cancelled"))


def test_tc_fr_035_16_reminder_reactivation_is_rejected_for_a_cancelled_examination(
    owner, owner_client
):
    """TC-FR-035-16 — Reminder reactivation is rejected for a cancelled examination."""
    assert_reactivation_rejected(owner_client, examination(owner, "cancelled"))


def test_tc_fr_035_17_reminder_creation_is_rejected_for_a_missed_examination(owner, owner_client):
    """TC-FR-035-17 — Reminder creation is rejected for a missed examination."""
    assert_creation_rejected(owner_client, examination(owner, "missed"))


def test_tc_fr_035_18_reminder_offset_update_is_rejected_for_a_missed_examination(
    owner, owner_client
):
    """TC-FR-035-18 — Reminder offset update is rejected for a missed examination."""
    assert_offset_update_rejected(owner_client, examination(owner, "missed"))


def test_tc_fr_035_19_reminder_reactivation_is_rejected_for_a_missed_examination(
    owner, owner_client
):
    """TC-FR-035-19 — Reminder reactivation is rejected for a missed examination."""
    assert_reactivation_rejected(owner_client, examination(owner, "missed"))


def test_tc_fr_036_01_reminder_due_date_is_calculated_from_the_scheduled_date_and_offset(
    owner, owner_client
):
    """TC-FR-036-01 — Reminder due date is calculated from the scheduled date and offset."""
    record = examination(owner, scheduled_date=date(2026, 8, 15))

    response = owner_client.post(reminder_url(record), {"offset_days": 7}, format="json")

    assert response.status_code == 201
    assert response.json()["due_date"] == "2026-08-08"
    assert Reminder.objects.get(examination=record).due_date == date(2026, 8, 8)


def test_tc_fr_036_02_reminder_due_date_recalculates_when_the_scheduled_date_changes(
    owner, owner_client
):
    """TC-FR-036-02 — Reminder due date recalculates when the scheduled date changes."""
    record = examination(owner, scheduled_date=date(2026, 8, 15))
    owner_client.post(reminder_url(record), {"offset_days": 7}, format="json")

    response = owner_client.patch(
        f"/api/v1/examinations/{record.pk}/", {"scheduled_date": "2026-09-01"}, format="json"
    )

    assert response.status_code == 200
    assert owner_client.get(reminder_url(record)).json()["due_date"] == "2026-08-25"


def test_tc_fr_036_03_reminder_due_date_recalculates_when_the_offset_changes(owner, owner_client):
    """TC-FR-036-03 — Reminder due date recalculates when the offset changes."""
    record = examination(owner, scheduled_date=date(2026, 8, 15))
    owner_client.post(reminder_url(record), {"offset_days": 7}, format="json")

    response = owner_client.patch(reminder_url(record), {"offset_days": 1}, format="json")

    assert response.status_code == 200
    assert response.json()["due_date"] == "2026-08-14"


def test_tc_fr_036_04_reminder_due_date_is_null_when_the_examination_has_no_scheduled_date(
    owner, owner_client
):
    """TC-FR-036-04 — Reminder due date is null when the examination has no scheduled date."""
    record = examination(owner, scheduled_date=date(2026, 8, 15))
    owner_client.post(reminder_url(record), {"offset_days": 7}, format="json")
    removed = owner_client.patch(
        f"/api/v1/examinations/{record.pk}/",
        {"status": "draft", "scheduled_date": None},
        format="json",
    )
    assert removed.status_code == 200

    response = owner_client.get(reminder_url(record))

    assert response.status_code == 200
    assert response.json()["due_date"] is None


def test_tc_sec_001_02_unauthenticated_requests_to_the_reminder_endpoint_are_rejected(
    owner, api_client
):
    """TC-SEC-001-02 — Unauthenticated requests to the reminder endpoint are rejected."""
    record = examination(owner)
    attach_reminder(record)

    response = api_client.get(reminder_url(record))

    assert response.status_code == 401


def test_tc_sec_002_04_a_user_cannot_attach_a_reminder_to_another_users_examination(
    owner, make_user, client_for
):
    """TC-SEC-002-04 — A user cannot attach a reminder to another user's examination."""
    record = examination(owner)
    intruder = client_for(make_user(email="intruder@example.com"))

    response = intruder.post(reminder_url(record), {"offset_days": 7}, format="json")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not found."}
    assert not Reminder.objects.filter(examination=record).exists()
    missing = intruder.post(
        "/api/v1/examinations/999999/reminder/", {"offset_days": 7}, format="json"
    )
    assert missing.content == response.content
