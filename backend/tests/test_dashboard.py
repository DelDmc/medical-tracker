"""The dashboard (Slice 16). The user's local date is frozen at 2026-08-04 (Warsaw)."""

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest
from freezegun import freeze_time

from examinations.models import ExaminationCategory, ExaminationRecord

pytestmark = pytest.mark.django_db

DASHBOARD_URL = "/api/v1/dashboard/"
LIST_URL = "/api/v1/examinations/"
TODAY = datetime(2026, 8, 4, 12, 0, tzinfo=ZoneInfo("Europe/Warsaw"))


def record(user, status, title=None, **fields):
    return ExaminationRecord.objects.create(
        user=user, title=title or f"A {status} record", status=status, **fields
    )


def completed(user, completed_date, title=None):
    return record(user, "completed", title, completed_date=completed_date)


def dashboard(client):
    with freeze_time(TODAY):
        response = client.get(DASHBOARD_URL)
    assert response.status_code == 200, response.content
    return response.json()


def collection(client, time_state):
    with freeze_time(TODAY):
        response = client.get(LIST_URL, {"time_state": time_state})
    assert response.status_code == 200
    return response.json()


def by_id(records):
    return sorted(records, key=lambda item: item["id"])


def recent_ids(client):
    return [item["id"] for item in dashboard(client)["recently_completed"]]


def test_tc_fr_044_01_the_dashboards_upcoming_collection_matches_the_shared_upcoming_query(
    owner, owner_client
):
    """TC-FR-044-01 — The dashboard's upcoming collection matches the shared upcoming query."""
    record(owner, "planned", scheduled_date=date(2026, 8, 10))
    record(owner, "planned", scheduled_date=date(2026, 8, 4))
    record(owner, "planned", scheduled_date=date(2026, 8, 3))  # overdue
    record(owner, "draft", scheduled_date=date(2026, 8, 20))

    upcoming = dashboard(owner_client)["upcoming"]

    assert len(upcoming) == 2
    assert by_id(upcoming) == by_id(collection(owner_client, "upcoming"))


def test_tc_fr_044_02_the_dashboards_overdue_collection_matches_the_shared_overdue_query(
    owner, owner_client
):
    """TC-FR-044-02 — The dashboard's overdue collection matches the shared overdue query."""
    record(owner, "planned", scheduled_date=date(2026, 8, 1))
    record(owner, "planned", scheduled_date=date(2026, 8, 4), scheduled_time=time(8, 0))
    record(owner, "planned", scheduled_date=date(2026, 8, 5))  # upcoming
    record(owner, "missed", scheduled_date=date(2026, 8, 1))

    overdue = dashboard(owner_client)["overdue"]

    assert len(overdue) == 2
    assert by_id(overdue) == by_id(collection(owner_client, "overdue"))


def test_tc_fr_044_03_an_eligible_record_appears_in_the_recently_completed_collection(
    owner, owner_client
):
    """TC-FR-044-03 — An eligible record appears in the dashboard's recently-completed collection."""
    eligible = completed(owner, date(2026, 7, 20))

    assert recent_ids(owner_client) == [eligible.pk]


def test_tc_fr_044_04_a_completion_date_29_days_before_today_is_included(owner, owner_client):
    """TC-FR-044-04 — A completion date exactly 29 days before today is included in recently completed."""
    boundary = completed(owner, date(2026, 7, 6))

    assert boundary.pk in recent_ids(owner_client)


def test_tc_fr_044_05_a_completion_date_equal_to_today_is_included(owner, owner_client):
    """TC-FR-044-05 — A completion date equal to today is included in recently completed."""
    today = completed(owner, date(2026, 8, 4))

    assert today.pk in recent_ids(owner_client)


def test_tc_fr_044_06_a_completion_date_30_days_before_today_is_excluded(owner, owner_client):
    """TC-FR-044-06 — A completion date 30 days before today is excluded from recently completed."""
    outside = completed(owner, date(2026, 7, 5))
    inside = completed(owner, date(2026, 7, 6))

    ids = recent_ids(owner_client)

    assert outside.pk not in ids
    assert inside.pk in ids


def test_tc_fr_044_07_recently_completed_is_ordered_by_completion_date_descending(
    owner, owner_client
):
    """TC-FR-044-07 — Recently completed is ordered by completion date descending."""
    middle = completed(owner, date(2026, 7, 20))
    latest = completed(owner, date(2026, 8, 2))
    earliest = completed(owner, date(2026, 7, 10))

    assert recent_ids(owner_client) == [latest.pk, middle.pk, earliest.pk]


def test_tc_fr_044_08_recently_completed_breaks_same_date_ties_by_identifier_descending(
    owner, owner_client
):
    """TC-FR-044-08 — Recently completed breaks same-date ties by identifier descending."""
    first = completed(owner, date(2026, 8, 1))
    second = completed(owner, date(2026, 8, 1))
    assert first.pk < second.pk

    assert recent_ids(owner_client) == [second.pk, first.pk]


def test_tc_fr_044_09_recently_completed_is_limited_to_five_records_without_pagination(
    owner, owner_client
):
    """TC-FR-044-09 — Recently completed is limited to five records without pagination."""
    records = [completed(owner, date(2026, 8, 4) - timedelta(days=offset)) for offset in range(7)]

    body = dashboard(owner_client)

    assert [item["id"] for item in body["recently_completed"]] == [r.pk for r in records[:5]]
    assert isinstance(body["recently_completed"], list)
    assert not {"count", "next", "previous", "results"} & set(body)


def test_tc_fr_045_01_status_counts_include_all_five_statuses(owner, owner_client, make_user):
    """TC-FR-045-01 — Status counts include all five statuses with correct and zero values."""
    record(owner, "planned", scheduled_date=date(2026, 8, 10))
    record(owner, "planned", scheduled_date=date(2026, 8, 12))
    record(owner, "draft")
    completed(owner, date(2026, 8, 1))
    record(make_user(), "missed", scheduled_date=date(2026, 8, 1))  # another user's

    assert dashboard(owner_client)["status_counts"] == {
        "draft": 1,
        "planned": 2,
        "completed": 1,
        "cancelled": 0,
        "missed": 0,
    }


def test_tc_fr_046_01_category_counts_include_every_system_category(owner, owner_client):
    """TC-FR-046-01 — Category counts include every system-defined category including zero values."""
    dental = ExaminationCategory.objects.get(slug="dental-appointment")
    vaccination = ExaminationCategory.objects.get(slug="vaccination")
    record(owner, "draft", category=dental)
    record(owner, "draft", category=dental)
    record(owner, "draft", category=vaccination)

    counts = {
        item["category"]["slug"]: item["count"]
        for item in dashboard(owner_client)["category_counts"]
    }

    assert set(counts) == set(ExaminationCategory.objects.values_list("slug", flat=True))
    assert len(counts) == 8
    assert counts["dental-appointment"] == 2
    assert counts["vaccination"] == 1
    assert sum(counts.values()) == 3
    assert counts["other"] == 0


def test_tc_fr_046_02_uncategorized_count_reflects_records_with_a_null_category(
    owner, owner_client
):
    """TC-FR-046-02 — Uncategorized count reflects records with a null category."""
    record(owner, "draft")
    record(owner, "planned", scheduled_date=date(2026, 8, 10))
    record(owner, "draft", category=ExaminationCategory.objects.get(slug="other"))

    assert dashboard(owner_client)["uncategorized_count"] == 2


def test_tc_fr_047_01_overdue_count_matches_the_shared_overdue_query(owner, owner_client):
    """TC-FR-047-01 — Overdue count matches the shared overdue query."""
    record(owner, "planned", scheduled_date=date(2026, 7, 1))
    record(owner, "planned", scheduled_date=date(2026, 8, 3))
    record(owner, "planned", scheduled_date=date(2026, 8, 4), scheduled_time=time(9, 0))
    record(owner, "planned", scheduled_date=date(2026, 8, 4))  # not overdue: no time
    record(owner, "cancelled", scheduled_date=date(2026, 7, 1))

    body = dashboard(owner_client)

    assert body["overdue_count"] == len(collection(owner_client, "overdue")) == 3
    assert body["overdue_count"] == len(body["overdue"])


def test_tc_sec_001_05_unauthenticated_requests_to_the_dashboard_endpoint_are_rejected(
    api_client,
):
    """TC-SEC-001-05 — Unauthenticated requests to the dashboard endpoint are rejected."""
    response = api_client.get(DASHBOARD_URL)

    assert response.status_code == 401
