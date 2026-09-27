"""The monthly-calendar endpoint (Slice 15)."""

from datetime import date

import pytest

from examinations.models import ExaminationRecord

pytestmark = pytest.mark.django_db

CALENDAR_URL = "/api/v1/calendar/"
AUGUST = {"start_date": "2026-08-01", "end_date": "2026-08-31"}


def record(user, status, **fields):
    return ExaminationRecord.objects.create(
        user=user, title=f"A {status} record", status=status, **fields
    )


def calendar_ids(client, params=AUGUST):
    response = client.get(CALENDAR_URL, params)
    assert response.status_code == 200, response.content
    return [entry["examination"]["id"] for entry in response.json()]


def assert_rejected_without_data(response):
    assert response.status_code == 400
    body = response.json()
    assert isinstance(body, dict)
    assert not any(key in body for key in ("calendar_date", "examination", "state"))


def test_tc_fr_019_03_a_dated_draft_is_excluded_from_calendar_results(owner, owner_client):
    """TC-FR-019-03 — A dated draft is excluded from calendar results."""
    draft = record(owner, "draft", scheduled_date=date(2026, 8, 15))
    planned = record(owner, "planned", scheduled_date=date(2026, 8, 15))

    ids = calendar_ids(owner_client)

    assert draft.pk not in ids
    assert planned.pk in ids


def test_tc_fr_042_05_a_draft_record_is_excluded_from_calendar_results(owner, owner_client):
    """TC-FR-042-05 — A draft record is excluded from calendar results."""
    draft = record(
        owner, "draft", scheduled_date=date(2026, 8, 10), completed_date=date(2026, 8, 12)
    )

    assert draft.pk not in calendar_ids(owner_client)


def test_tc_fr_042_06_a_record_missing_its_required_display_date_is_excluded(owner, owner_client):
    """TC-FR-042-06 — A record missing its required display date is excluded from calendar results."""
    # Stored directly: validation would not let a completed record lack its date.
    undated = record(owner, "completed", scheduled_date=date(2026, 8, 10), completed_date=None)
    dated = record(owner, "completed", completed_date=date(2026, 8, 10))

    ids = calendar_ids(owner_client)

    assert undated.pk not in ids
    assert dated.pk in ids


def test_tc_fr_042_07_a_missing_date_range_parameter_is_rejected(owner, owner_client):
    """TC-FR-042-07 — A missing date-range parameter is rejected."""
    record(owner, "planned", scheduled_date=date(2026, 8, 15))

    for params in ({"start_date": "2026-08-01"}, {"end_date": "2026-08-31"}, {}):
        assert_rejected_without_data(owner_client.get(CALENDAR_URL, params))


def test_tc_fr_042_08_a_malformed_date_range_parameter_is_rejected(owner, owner_client):
    """TC-FR-042-08 — A malformed date-range parameter is rejected."""
    record(owner, "planned", scheduled_date=date(2026, 8, 15))

    for malformed in ("not-a-date", "2026-13-01", "2026-02-30", "20260801", "01.08.2026"):
        response = owner_client.get(
            CALENDAR_URL, {"start_date": malformed, "end_date": "2026-08-31"}
        )
        assert_rejected_without_data(response)
        assert response.json()["start_date"]


def test_tc_fr_042_09_a_start_date_after_the_end_date_is_rejected(owner, owner_client):
    """TC-FR-042-09 — A start date after the end date is rejected."""
    record(owner, "planned", scheduled_date=date(2026, 8, 15))

    response = owner_client.get(
        CALENDAR_URL, {"start_date": "2026-08-31", "end_date": "2026-08-01"}
    )

    assert_rejected_without_data(response)


def test_tc_sec_001_04_unauthenticated_requests_to_the_calendar_endpoint_are_rejected(
    api_client,
):
    """TC-SEC-001-04 — Unauthenticated requests to the calendar endpoint are rejected."""
    response = api_client.get(CALENDAR_URL, AUGUST)

    assert response.status_code == 401
