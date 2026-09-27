"""Reminder deactivation on status change and the due-reminders query (Slice 12)."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest
from freezegun import freeze_time

from examinations.models import ExaminationRecord, Reminder

pytestmark = pytest.mark.django_db

DUE_URL = "/api/v1/reminders/"
TODAY_IN_WARSAW = datetime(2026, 8, 4, 12, 0, tzinfo=ZoneInfo("Europe/Warsaw"))


def planned_with_active_reminder(user, scheduled_date=date(2026, 8, 20)):
    record = ExaminationRecord.objects.create(
        user=user, title="Planned examination", status="planned", scheduled_date=scheduled_date
    )
    reminder = Reminder.objects.create(examination=record, offset_days=7, is_active=True)
    return record, reminder


def patch_examination(client, record, changes):
    response = client.patch(f"/api/v1/examinations/{record.pk}/", changes, format="json")
    assert response.status_code == 200, response.content
    return response


def test_tc_fr_037_02_the_due_state_filter_returns_only_due_active_reminders(
    owner, owner_client, make_user
):
    """TC-FR-037-02 — The reminders endpoint's due-state filter returns only due, active reminders."""
    _, due_active = planned_with_active_reminder(owner, date(2026, 8, 10))  # due 2026-08-03
    _, future_active = planned_with_active_reminder(owner, date(2026, 8, 20))  # due 2026-08-13
    _, due_inactive = planned_with_active_reminder(owner, date(2026, 8, 10))
    Reminder.objects.filter(pk=due_inactive.pk).update(is_active=False)
    planned_with_active_reminder(make_user(), date(2026, 8, 10))  # another user's

    with freeze_time(TODAY_IN_WARSAW):
        response = owner_client.get(DUE_URL, {"state": "due"})

    assert response.status_code == 200
    assert [reminder["id"] for reminder in response.json()] == [due_active.pk]
    assert response.json()[0]["due_date"] == "2026-08-03"
    assert owner_client.get(DUE_URL, {"state": "overdue"}).status_code == 400


def assert_deactivated_by(client, user, changes):
    record, reminder = planned_with_active_reminder(user)

    response = patch_examination(client, record, changes)

    assert response.json()["status"] == changes["status"]
    # The same PATCH request already left the reminder inactive.
    assert Reminder.objects.get(pk=reminder.pk).is_active is False


def test_tc_fr_038_01_changing_a_planned_examination_to_draft_deactivates_its_reminder(
    owner, owner_client
):
    """TC-FR-038-01 — Changing a planned examination to draft deactivates its reminder."""
    assert_deactivated_by(owner_client, owner, {"status": "draft"})


def test_tc_fr_038_02_changing_a_planned_examination_to_completed_deactivates_its_reminder(
    owner, owner_client
):
    """TC-FR-038-02 — Changing a planned examination to completed deactivates its reminder."""
    with freeze_time(TODAY_IN_WARSAW):
        assert_deactivated_by(
            owner_client, owner, {"status": "completed", "completed_date": "2026-08-04"}
        )


def test_tc_fr_038_03_changing_a_planned_examination_to_cancelled_deactivates_its_reminder(
    owner, owner_client
):
    """TC-FR-038-03 — Changing a planned examination to cancelled deactivates its reminder."""
    assert_deactivated_by(owner_client, owner, {"status": "cancelled"})


def test_tc_fr_038_04_changing_a_planned_examination_to_missed_deactivates_its_reminder(
    owner, owner_client
):
    """TC-FR-038-04 — Changing a planned examination to missed deactivates its reminder."""
    assert_deactivated_by(owner_client, owner, {"status": "missed"})


def test_tc_fr_038_05_returning_an_examination_to_planned_does_not_reactivate_its_reminder(
    owner, owner_client
):
    """TC-FR-038-05 — Returning an examination to planned does not reactivate its reminder."""
    record, reminder = planned_with_active_reminder(owner)
    patch_examination(owner_client, record, {"status": "cancelled"})
    assert Reminder.objects.get(pk=reminder.pk).is_active is False

    patch_examination(owner_client, record, {"status": "planned", "scheduled_date": "2026-09-01"})

    reminder = Reminder.objects.get(pk=reminder.pk)
    assert reminder.is_active is False
    assert reminder.due_date == date(2026, 8, 25)
