"""Monthly-calendar placement (ADS-FR-042-01, domain_model.md §6.5)."""

from datetime import date, datetime

from django.db.models import QuerySet

from .models import ExaminationStatus
from .time_state import OVERDUE, time_state_for

PLACED_ON_SCHEDULED_DATE = [
    ExaminationStatus.PLANNED,
    ExaminationStatus.CANCELLED,
    ExaminationStatus.MISSED,
]


def calendar_entries(queryset: QuerySet, start: date, end: date, local_now: datetime) -> list:
    """Entries whose status-specific display date falls within `start`..`end`.

    Planned, cancelled and missed records sit on `scheduled_date`; completed ones on
    `completed_date`. Drafts, and records without the date their status needs, are
    excluded. A planned record the overdue rule matches has state `overdue`; every
    other entry's state is its stored status.
    """
    records = queryset.exclude(status=ExaminationStatus.DRAFT)
    placed = [
        (record.scheduled_date, record)
        for record in records.filter(
            status__in=PLACED_ON_SCHEDULED_DATE, scheduled_date__range=(start, end)
        )
    ] + [
        (record.completed_date, record)
        for record in records.filter(
            status=ExaminationStatus.COMPLETED, completed_date__range=(start, end)
        )
    ]
    placed.sort(
        key=lambda item: (
            item[0],
            item[1].scheduled_time is None,
            item[1].scheduled_time or datetime.min.time(),
            item[1].pk,
        )
    )
    return [
        {
            "calendar_date": calendar_date,
            "state": OVERDUE if time_state_for(record, local_now) == OVERDUE else record.status,
            "examination": record,
        }
        for calendar_date, record in placed
    ]
