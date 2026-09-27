"""Past, upcoming and overdue collections (Slice 10).

Every case freezes the user's *local* clock in their own timezone: Europe/Warsaw
(UTC+2 in August) throughout, and America/Los_Angeles in TC-FR-033-04, where 20:00
local time is already the next day in UTC.
"""

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest
from freezegun import freeze_time

from examinations.models import ExaminationRecord

pytestmark = pytest.mark.django_db

LIST_URL = "/api/v1/examinations/"


def local_clock(timezone, local_iso):
    """Freeze the clock at `local_iso` wall-clock time in `timezone`."""
    return freeze_time(datetime.fromisoformat(local_iso).replace(tzinfo=ZoneInfo(timezone)))


def warsaw(local_iso="2026-08-04T12:00"):
    return local_clock("Europe/Warsaw", local_iso)


def record(user, status, **fields):
    return ExaminationRecord.objects.create(
        user=user, title=f"A {status} record", status=status, **fields
    )


def collection(client, time_state):
    response = client.get(LIST_URL, {"time_state": time_state})
    assert response.status_code == 200, response.content
    return {item["id"]: item for item in response.json()}


def test_tc_fr_019_01_a_dated_draft_is_excluded_from_upcoming_results(owner, owner_client):
    """TC-FR-019-01 — A dated draft is excluded from upcoming results."""
    draft = record(owner, "draft", scheduled_date=date(2026, 8, 20))
    planned = record(owner, "planned", scheduled_date=date(2026, 8, 20))
    with warsaw():
        upcoming = collection(owner_client, "upcoming")

    assert draft.pk not in upcoming
    assert planned.pk in upcoming


def test_tc_fr_019_02_a_dated_draft_is_excluded_from_overdue_results(owner, owner_client):
    """TC-FR-019-02 — A dated draft is excluded from overdue results."""
    draft = record(owner, "draft", scheduled_date=date(2026, 7, 1))
    planned = record(owner, "planned", scheduled_date=date(2026, 7, 1))
    with warsaw():
        overdue = collection(owner_client, "overdue")

    assert draft.pk not in overdue
    assert planned.pk in overdue


def test_tc_fr_031_01_a_completed_record_is_included_in_the_past_collection_by_completion_date(
    owner, owner_client
):
    """TC-FR-031-01 — A completed record is included in the past collection by completion date."""
    completed = record(
        owner, "completed", completed_date=date(2026, 8, 4), scheduled_date=date(2026, 9, 1)
    )
    with warsaw():
        past = collection(owner_client, "past")

    assert completed.pk in past
    assert past[completed.pk]["time_state"] is None


def test_tc_fr_031_02_a_cancelled_record_is_included_in_the_past_collection_by_scheduled_date(
    owner, owner_client
):
    """TC-FR-031-02 — A cancelled record is included in the past collection by scheduled date."""
    cancelled = record(owner, "cancelled", scheduled_date=date(2026, 8, 3))
    with warsaw():
        past = collection(owner_client, "past")

    assert cancelled.pk in past


def test_tc_fr_031_03_a_missed_record_is_included_in_the_past_collection_by_scheduled_date(
    owner, owner_client
):
    """TC-FR-031-03 — A missed record is included in the past collection by scheduled date."""
    missed = record(owner, "missed", scheduled_date=date(2026, 8, 3))
    with warsaw():
        past = collection(owner_client, "past")

    assert missed.pk in past


def test_tc_fr_031_04_a_planned_record_is_excluded_from_the_past_collection(owner, owner_client):
    """TC-FR-031-04 — A planned record is excluded from the past collection."""
    planned = record(owner, "planned", scheduled_date=date(2026, 8, 3))
    with warsaw():
        past = collection(owner_client, "past")

    assert planned.pk not in past


def test_tc_fr_031_05_a_draft_record_is_excluded_from_the_past_collection(owner, owner_client):
    """TC-FR-031-05 — A draft record is excluded from the past collection."""
    draft = record(owner, "draft", scheduled_date=date(2026, 8, 3), completed_date=date(2026, 8, 3))
    with warsaw():
        past = collection(owner_client, "past")

    assert draft.pk not in past


def test_tc_fr_031_06_a_completed_record_with_a_future_completion_date_is_excluded_from_past(
    owner, owner_client
):
    """TC-FR-031-06 — A completed record with a future completion date is excluded from the past collection."""
    # Validation rejects this record through the API; it is stored directly to prove the
    # query excludes it on its own.
    future = record(owner, "completed", completed_date=date(2026, 8, 5))
    with warsaw():
        past = collection(owner_client, "past")

    assert future.pk not in past


def test_tc_fr_032_01_a_future_dated_planned_record_is_included_in_upcoming(owner, owner_client):
    """TC-FR-032-01 — A future-dated planned record is included in upcoming."""
    planned = record(owner, "planned", scheduled_date=date(2026, 8, 10))
    with warsaw():
        upcoming = collection(owner_client, "upcoming")

    assert planned.pk in upcoming
    assert upcoming[planned.pk]["time_state"] == "upcoming"


def test_tc_fr_032_02_a_current_date_planned_record_without_a_time_is_included_in_upcoming(
    owner, owner_client
):
    """TC-FR-032-02 — A current-date planned record without a scheduled time is included in upcoming."""
    planned = record(owner, "planned", scheduled_date=date(2026, 8, 4))
    with warsaw("2026-08-04T23:30"):
        upcoming = collection(owner_client, "upcoming")

    assert planned.pk in upcoming


def test_tc_fr_032_03_a_current_date_planned_record_with_an_unpassed_time_is_in_upcoming(
    owner, owner_client
):
    """TC-FR-032-03 — A current-date planned record with an unpassed scheduled time is included in upcoming."""
    planned = record(owner, "planned", scheduled_date=date(2026, 8, 4), scheduled_time=time(11, 0))
    with warsaw("2026-08-04T09:00"):
        upcoming = collection(owner_client, "upcoming")

    assert planned.pk in upcoming
    assert upcoming[planned.pk]["time_state"] == "upcoming"


def test_tc_fr_032_04_an_overdue_planned_record_is_excluded_from_upcoming(owner, owner_client):
    """TC-FR-032-04 — An overdue planned record is excluded from upcoming."""
    overdue = record(owner, "planned", scheduled_date=date(2026, 8, 3))
    with warsaw():
        upcoming = collection(owner_client, "upcoming")

    assert overdue.pk not in upcoming


def test_tc_fr_032_05_a_completed_record_is_excluded_from_upcoming(owner, owner_client):
    """TC-FR-032-05 — A completed record is excluded from upcoming."""
    completed = record(
        owner, "completed", completed_date=date(2026, 8, 3), scheduled_date=date(2026, 8, 10)
    )
    with warsaw():
        upcoming = collection(owner_client, "upcoming")

    assert completed.pk not in upcoming


def test_tc_fr_033_01_a_planned_record_scheduled_before_the_local_date_is_overdue(
    owner, owner_client
):
    """TC-FR-033-01 — A planned record scheduled before the current local date is overdue."""
    planned = record(owner, "planned", scheduled_date=date(2026, 8, 3))
    with warsaw("2026-08-04T00:30"):
        overdue = collection(owner_client, "overdue")

    assert planned.pk in overdue
    assert overdue[planned.pk]["time_state"] == "overdue"


def test_tc_fr_033_02_a_current_date_planned_record_whose_time_has_passed_is_overdue(
    owner, owner_client
):
    """TC-FR-033-02 — A current-date planned record whose scheduled time has passed is overdue."""
    planned = record(owner, "planned", scheduled_date=date(2026, 8, 4), scheduled_time=time(9, 0))
    with warsaw("2026-08-04T11:00"):
        overdue = collection(owner_client, "overdue")

    assert planned.pk in overdue


def test_tc_fr_033_03_a_current_date_planned_record_whose_time_has_not_passed_is_not_overdue(
    owner, owner_client
):
    """TC-FR-033-03 — A current-date planned record whose scheduled time has not passed is not overdue."""
    planned = record(owner, "planned", scheduled_date=date(2026, 8, 4), scheduled_time=time(11, 0))
    with warsaw("2026-08-04T09:00"):
        overdue = collection(owner_client, "overdue")

    assert planned.pk not in overdue


def test_tc_fr_033_04_a_current_date_planned_record_without_a_time_is_not_overdue(
    make_user, client_for
):
    """TC-FR-033-04 — A current-date planned record without a scheduled time is not overdue."""
    user = make_user(timezone="America/Los_Angeles")
    planned = record(user, "planned", scheduled_date=date(2026, 8, 4))
    # 20:00 on 2026-08-04 in Los Angeles is 03:00 on 2026-08-05 in UTC.
    with local_clock("America/Los_Angeles", "2026-08-04T20:00"):
        overdue = collection(client_for(user), "overdue")
        upcoming = collection(client_for(user), "upcoming")

    assert planned.pk not in overdue
    assert upcoming[planned.pk]["time_state"] == "upcoming"


def test_tc_fr_033_05_the_same_unchanged_record_changes_state_as_time_passes_its_boundary(
    owner, owner_client
):
    """TC-FR-033-05 — The same unchanged record's derived state changes as time passes its boundary."""
    planned = record(owner, "planned", scheduled_date=date(2026, 8, 4), scheduled_time=time(9, 0))
    stored = ExaminationRecord.objects.values().get(pk=planned.pk)

    with warsaw("2026-08-04T08:59"):
        before = collection(owner_client, "overdue")
    with warsaw("2026-08-04T09:01"):
        after = collection(owner_client, "overdue")

    assert planned.pk not in before
    assert planned.pk in after
    assert ExaminationRecord.objects.values().get(pk=planned.pk) == stored


def test_tc_fr_034_01_only_the_planned_record_among_past_dated_records_is_overdue(
    owner, owner_client
):
    """TC-FR-034-01 — Only the planned record among same-dated records of every status is overdue."""
    past_date = date(2026, 8, 1)
    records = {
        status: record(owner, status, scheduled_date=past_date, completed_date=past_date)
        for status in ("draft", "planned", "completed", "cancelled", "missed")
    }
    with warsaw():
        overdue = collection(owner_client, "overdue")

    assert set(overdue) == {records["planned"].pk}
