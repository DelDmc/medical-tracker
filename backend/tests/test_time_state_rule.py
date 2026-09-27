"""The derived time-state rule has one meaning everywhere (Task 10.1 acceptance).

A supporting consistency check, not a test case of docs/test_specification.md: the
record-level `time_state_for` and the queryset filters in examinations/time_state.py
must never disagree for the same record and clock.
"""

import itertools
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest

from examinations.models import ExaminationRecord, ExaminationStatus
from examinations.time_state import (
    OVERDUE,
    UPCOMING,
    overdue_queryset,
    past_queryset,
    time_state_for,
    upcoming_queryset,
)

pytestmark = pytest.mark.django_db

DATES = [None, date(2026, 8, 3), date(2026, 8, 4), date(2026, 8, 5)]
TIMES = [None, time(8, 59), time(9, 0), time(9, 1)]
CLOCKS = [
    datetime(2026, 8, 4, 9, 0, 0, tzinfo=ZoneInfo("Europe/Warsaw")),
    datetime(2026, 8, 4, 9, 0, 30, tzinfo=ZoneInfo("Europe/Warsaw")),
    datetime(2026, 8, 4, 0, 0, 0, tzinfo=ZoneInfo("Europe/Warsaw")),
    datetime(2026, 8, 4, 23, 59, 59, tzinfo=ZoneInfo("Europe/Warsaw")),
]


def test_time_state_for_and_the_collection_querysets_never_disagree(owner):
    for status, scheduled_date, scheduled_time in itertools.product(
        ExaminationStatus.values, DATES, TIMES
    ):
        ExaminationRecord.objects.create(
            user=owner,
            title=f"{status} {scheduled_date} {scheduled_time}",
            status=status,
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time,
            completed_date=scheduled_date,
        )
    records = ExaminationRecord.objects.filter(user=owner)

    for local_now in CLOCKS:
        overdue = set(overdue_queryset(records, local_now).values_list("pk", flat=True))
        upcoming = set(upcoming_queryset(records, local_now).values_list("pk", flat=True))
        past = set(past_queryset(records, local_now).values_list("pk", flat=True))
        assert not overdue & upcoming
        assert not (overdue | upcoming) & past
        for record in records:
            state = time_state_for(record, local_now)
            assert (record.pk in overdue) == (state == OVERDUE), (record.title, local_now)
            assert (record.pk in upcoming) == (state == UPCOMING), (record.title, local_now)
