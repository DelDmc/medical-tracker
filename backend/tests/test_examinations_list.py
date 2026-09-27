"""List search, filters and ordering (Slice 9)."""

from datetime import date

import pytest

from examinations.models import ExaminationCategory, ExaminationRecord

pytestmark = pytest.mark.django_db

LIST_URL = "/api/v1/examinations/"


def make_record(user, title, **fields):
    defaults = {"status": "planned", "scheduled_date": date(2026, 9, 15)}
    return ExaminationRecord.objects.create(user=user, title=title, **{**defaults, **fields})


def titles(response):
    assert response.status_code == 200, response.content
    return [record["title"] for record in response.json()]


def category(slug):
    return ExaminationCategory.objects.get(slug=slug)


def test_tc_fr_028_01_title_search_performs_a_case_insensitive_containment_match(
    owner, owner_client, make_user
):
    """TC-FR-028-01 — Title search performs a case-insensitive containment match."""
    make_record(owner, "Annual dental checkup")
    make_record(owner, "Eye exam")
    make_record(make_user(), "Someone else's dental visit")

    assert titles(owner_client.get(LIST_URL, {"search": "dental"})) == ["Annual dental checkup"]
    assert titles(owner_client.get(LIST_URL, {"search": "DENTAL"})) == ["Annual dental checkup"]


def test_tc_fr_029_01_the_status_filter_returns_only_matching_records(owner, owner_client):
    """TC-FR-029-01 — The status filter returns only matching records."""
    make_record(owner, "Planned visit", status="planned")
    make_record(owner, "Completed visit", status="completed", completed_date=date(2026, 7, 1))

    assert titles(owner_client.get(LIST_URL, {"status": "planned"})) == ["Planned visit"]
    invalid = owner_client.get(LIST_URL, {"status": "archived"})
    assert invalid.status_code == 400
    assert invalid.json()["status"]


def test_tc_fr_029_02_the_category_filter_returns_only_matching_records(owner, owner_client):
    """TC-FR-029-02 — The category filter returns only matching records."""
    dental = category("dental-appointment")
    make_record(owner, "Dentist", category=dental)
    make_record(owner, "Vaccine", category=category("vaccination"))
    make_record(owner, "Unfiled")

    assert titles(owner_client.get(LIST_URL, {"category": dental.pk})) == ["Dentist"]
    assert owner_client.get(LIST_URL, {"category": 9999}).status_code == 400


def test_tc_fr_029_03_combined_status_and_category_filters_use_and_semantics(owner, owner_client):
    """TC-FR-029-03 — Combined status and category filters use AND semantics."""
    dental, vaccination = category("dental-appointment"), category("vaccination")
    for status in ("planned", "missed"):
        for chosen in (dental, vaccination):
            make_record(owner, f"{status} {chosen.slug}", status=status, category=chosen)

    response = owner_client.get(LIST_URL, {"status": "planned", "category": dental.pk})

    assert titles(response) == ["planned dental-appointment"]


def test_tc_fr_030_01_ascending_scheduled_date_ordering_places_undated_records_last(
    owner, owner_client
):
    """TC-FR-030-01 — Ascending scheduled-date ordering places undated records last."""
    make_record(owner, "Undated draft", status="draft", scheduled_date=None)
    make_record(owner, "October", scheduled_date=date(2026, 10, 1))
    make_record(owner, "Another undated", status="draft", scheduled_date=None)
    make_record(owner, "August", scheduled_date=date(2026, 8, 1))
    make_record(owner, "September", scheduled_date=date(2026, 9, 1))

    ordered = titles(owner_client.get(LIST_URL, {"ordering": "scheduled_date"}))

    assert ordered == ["August", "September", "October", "Undated draft", "Another undated"]


def test_tc_fr_030_02_descending_scheduled_date_ordering_places_undated_records_last(
    owner, owner_client
):
    """TC-FR-030-02 — Descending scheduled-date ordering places undated records last."""
    make_record(owner, "Undated draft", status="draft", scheduled_date=None)
    make_record(owner, "August", scheduled_date=date(2026, 8, 1))
    make_record(owner, "October", scheduled_date=date(2026, 10, 1))
    make_record(owner, "Another undated", status="draft", scheduled_date=None)
    make_record(owner, "September", scheduled_date=date(2026, 9, 1))

    ordered = titles(owner_client.get(LIST_URL, {"ordering": "-scheduled_date"}))

    assert ordered == ["October", "September", "August", "Undated draft", "Another undated"]
    assert owner_client.get(LIST_URL, {"ordering": "title"}).status_code == 400


def test_tc_fr_030_03_records_sharing_the_same_scheduled_date_use_a_deterministic_tiebreak(
    owner, owner_client
):
    """TC-FR-030-03 — Records sharing the same scheduled date use a deterministic tiebreak."""
    first = make_record(owner, "First created", scheduled_date=date(2026, 9, 1))
    second = make_record(owner, "Second created", scheduled_date=date(2026, 9, 1))
    assert first.pk < second.pk

    for ordering in ("scheduled_date", "-scheduled_date"):
        observed = {
            tuple(titles(owner_client.get(LIST_URL, {"ordering": ordering}))) for _ in range(5)
        }
        assert observed == {("First created", "Second created")}
