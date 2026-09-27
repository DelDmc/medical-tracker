"""Recurrence rules and next-due-date arithmetic (Slice 13)."""

from datetime import date

import pytest
from freezegun import freeze_time

from examinations.models import ExaminationRecord, RecurrenceRule

pytestmark = pytest.mark.django_db


def recurrence_url(examination):
    return f"/api/v1/examinations/{examination.pk}/recurrence/"


def examination(user, status="planned", scheduled_date=date(2026, 3, 15), **fields):
    if status == "completed":
        fields.setdefault("completed_date", date(2026, 3, 15))
    return ExaminationRecord.objects.create(
        user=user,
        title=f"A {status} examination",
        status=status,
        scheduled_date=scheduled_date,
        **fields,
    )


def attach_rule(record, interval="monthly"):
    return RecurrenceRule.objects.create(examination=record, interval=interval)


def assert_business_rule_error(response):
    assert response.status_code == 400, response.content
    assert response.json()["non_field_errors"]


def create_rule(client, record, interval):
    return client.post(recurrence_url(record), {"interval": interval}, format="json")


def next_due(client, record):
    response = client.get(recurrence_url(record))
    assert response.status_code == 200, response.content
    return response.json()["next_due_date"]


def test_tc_fr_018_01_recurrence_creation_is_rejected_for_a_draft_examination(owner, owner_client):
    """TC-FR-018-01 — Recurrence creation is rejected for a draft examination."""
    draft = examination(owner, "draft")

    assert_business_rule_error(create_rule(owner_client, draft, "yearly"))
    assert not RecurrenceRule.objects.filter(examination=draft).exists()


def test_tc_fr_018_02_recurrence_update_is_rejected_for_a_draft_examination(owner, owner_client):
    """TC-FR-018-02 — Recurrence update is rejected for a draft examination."""
    draft = examination(owner, "draft")
    rule = attach_rule(draft, "monthly")

    response = owner_client.patch(recurrence_url(draft), {"interval": "yearly"}, format="json")

    assert_business_rule_error(response)
    assert RecurrenceRule.objects.get(pk=rule.pk).interval == "monthly"


@pytest.fixture
def planned(owner):
    return examination(owner)


def assert_interval_accepted(client, record, interval):
    response = create_rule(client, record, interval)
    assert response.status_code == 201, response.content
    assert response.json()["interval"] == interval
    assert RecurrenceRule.objects.get(examination=record).interval == interval


def test_tc_fr_039_01_a_monthly_recurrence_interval_is_accepted(planned, owner_client):
    """TC-FR-039-01 — A monthly recurrence interval is accepted for a planned examination."""
    assert_interval_accepted(owner_client, planned, "monthly")


def test_tc_fr_039_02_a_six_month_recurrence_interval_is_accepted(planned, owner_client):
    """TC-FR-039-02 — A six-month recurrence interval is accepted for a planned examination."""
    assert_interval_accepted(owner_client, planned, "six_months")


def test_tc_fr_039_03_a_yearly_recurrence_interval_is_accepted(planned, owner_client):
    """TC-FR-039-03 — A yearly recurrence interval is accepted for a planned examination."""
    assert_interval_accepted(owner_client, planned, "yearly")


def test_tc_fr_039_04_an_unsupported_recurrence_interval_is_rejected(planned, owner_client):
    """TC-FR-039-04 — An unsupported recurrence interval is rejected."""
    response = create_rule(owner_client, planned, "weekly")

    assert response.status_code == 400
    assert response.json()["interval"]
    assert not RecurrenceRule.objects.filter(examination=planned).exists()


def assert_creation_rejected(client, record):
    assert_business_rule_error(create_rule(client, record, "yearly"))
    assert not RecurrenceRule.objects.filter(examination=record).exists()


def test_tc_fr_039_05_recurrence_creation_is_rejected_for_a_draft_examination(owner, owner_client):
    """TC-FR-039-05 — Recurrence creation is rejected for a draft examination."""
    assert_creation_rejected(owner_client, examination(owner, "draft"))


def test_tc_fr_039_06_recurrence_creation_is_rejected_for_a_completed_examination(
    owner, owner_client
):
    """TC-FR-039-06 — Recurrence creation is rejected for a completed examination."""
    assert_creation_rejected(owner_client, examination(owner, "completed"))


def test_tc_fr_039_07_recurrence_creation_is_rejected_for_a_cancelled_examination(
    owner, owner_client
):
    """TC-FR-039-07 — Recurrence creation is rejected for a cancelled examination."""
    assert_creation_rejected(owner_client, examination(owner, "cancelled"))


def test_tc_fr_039_08_recurrence_creation_is_rejected_for_a_missed_examination(owner, owner_client):
    """TC-FR-039-08 — Recurrence creation is rejected for a missed examination."""
    assert_creation_rejected(owner_client, examination(owner, "missed"))


def complete(client, record):
    with freeze_time("2026-08-04T12:00:00+00:00"):
        response = client.patch(
            f"/api/v1/examinations/{record.pk}/",
            {"status": "completed", "completed_date": "2026-08-04"},
            format="json",
        )
    assert response.status_code == 200, response.content


def test_tc_fr_039_09_an_existing_recurrence_rule_remains_attached_across_status_changes(
    planned, owner_client
):
    """TC-FR-039-09 — An existing recurrence rule remains attached and unchanged across status changes."""
    assert create_rule(owner_client, planned, "yearly").status_code == 201
    rule = RecurrenceRule.objects.get(examination=planned)

    complete(owner_client, planned)

    retained = RecurrenceRule.objects.get(examination=planned)
    assert retained.pk == rule.pk
    assert retained.interval == "yearly"
    assert retained.updated_at == rule.updated_at
    assert owner_client.get(recurrence_url(planned)).json()["interval"] == "yearly"


def test_tc_fr_039_10_recurrence_update_is_rejected_once_the_examination_is_no_longer_planned(
    planned, owner_client
):
    """TC-FR-039-10 — Recurrence update is rejected once the examination is no longer planned."""
    assert create_rule(owner_client, planned, "monthly").status_code == 201
    complete(owner_client, planned)

    response = owner_client.patch(recurrence_url(planned), {"interval": "yearly"}, format="json")

    assert_business_rule_error(response)
    assert RecurrenceRule.objects.get(examination=planned).interval == "monthly"


def assert_next_due(client, user, scheduled_date, interval, expected):
    record = examination(user, scheduled_date=scheduled_date)
    assert create_rule(client, record, interval).status_code == 201
    assert next_due(client, record) == expected


def test_tc_fr_040_01_monthly_recurrence_adds_one_calendar_month(owner, owner_client):
    """TC-FR-040-01 — Monthly recurrence adds one calendar month."""
    assert_next_due(owner_client, owner, date(2026, 3, 15), "monthly", "2026-04-15")


def test_tc_fr_040_02_six_month_recurrence_adds_six_calendar_months(owner, owner_client):
    """TC-FR-040-02 — Six-month recurrence adds six calendar months."""
    assert_next_due(owner_client, owner, date(2026, 3, 15), "six_months", "2026-09-15")


def test_tc_fr_040_03_yearly_recurrence_adds_one_calendar_year(owner, owner_client):
    """TC-FR-040-03 — Yearly recurrence adds one calendar year."""
    assert_next_due(owner_client, owner, date(2026, 3, 15), "yearly", "2027-03-15")


def test_tc_fr_040_04_a_month_end_source_date_clamps_to_the_target_months_last_valid_day(
    owner, owner_client
):
    """TC-FR-040-04 — A month-end source date clamps to the target month's last valid day."""
    assert_next_due(owner_client, owner, date(2026, 1, 31), "monthly", "2026-02-28")


def test_tc_fr_040_05_yearly_recurrence_from_february_29_resolves_to_february_28(
    owner, owner_client
):
    """TC-FR-040-05 — Yearly recurrence from February 29 resolves to February 28 in a non-leap year."""
    assert_next_due(owner_client, owner, date(2028, 2, 29), "yearly", "2029-02-28")


def test_tc_fr_040_06_next_due_date_is_null_when_the_source_has_no_scheduled_date(
    planned, owner_client
):
    """TC-FR-040-06 — Next due date is null when the source has no scheduled date."""
    assert create_rule(owner_client, planned, "monthly").status_code == 201
    removed = owner_client.patch(
        f"/api/v1/examinations/{planned.pk}/",
        {"status": "draft", "scheduled_date": None},
        format="json",
    )
    assert removed.status_code == 200

    assert next_due(owner_client, planned) is None


def test_tc_sec_001_03_unauthenticated_requests_to_the_recurrence_endpoint_are_rejected(
    planned, api_client
):
    """TC-SEC-001-03 — Unauthenticated requests to the recurrence endpoint are rejected."""
    attach_rule(planned)

    response = api_client.get(recurrence_url(planned))

    assert response.status_code == 401


def test_tc_sec_002_05_a_user_cannot_attach_a_recurrence_rule_to_another_users_examination(
    planned, make_user, client_for
):
    """TC-SEC-002-05 — A user cannot attach a recurrence rule to another user's examination."""
    intruder = client_for(make_user(email="intruder@example.com"))

    response = create_rule(intruder, planned, "yearly")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not found."}
    assert not RecurrenceRule.objects.filter(examination=planned).exists()
