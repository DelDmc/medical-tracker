"""The derived time state of an examination: the single source of truth.

`overdue` is never stored (ADS-FR-033-01). It is derived from `status`,
`scheduled_date`, the optional `scheduled_time` and the user's current local date
and time (ADS-FR-033-02, ADS-FR-034-01; domain_model.md §6.2-§6.3):

    overdue  = planned AND (scheduled_date <  today
                            OR (scheduled_date = today
                                AND scheduled_time is not null
                                AND scheduled_time < now))
    upcoming = planned AND not overdue

A current-date record without a scheduled time is upcoming, never overdue. Every
record that is not planned — drafts included — has no time state.

Everything that needs this rule — the `time_state` field, the list filters, the
calendar `state` and the dashboard — uses this module.
"""

from datetime import date, datetime, time

from django.db.models import Q, QuerySet

from .models import ExaminationStatus

UPCOMING = "upcoming"
OVERDUE = "overdue"
PAST = "past"
COLLECTIONS = (PAST, UPCOMING, OVERDUE)


def local_clock(local_now: datetime) -> tuple[date, time]:
    """The user's local date and wall-clock time, to whole seconds."""
    return local_now.date(), local_now.time().replace(microsecond=0)


def time_state_for(record, local_now: datetime) -> str | None:
    """`"upcoming"`, `"overdue"`, or `None` for `record` at the user's `local_now`."""
    if record.status != ExaminationStatus.PLANNED or record.scheduled_date is None:
        return None
    today, current_time = local_clock(local_now)
    if record.scheduled_date < today:
        return OVERDUE
    if (
        record.scheduled_date == today
        and record.scheduled_time is not None
        and record.scheduled_time < current_time
    ):
        return OVERDUE
    return UPCOMING


# ---- Collections: the same rule as `time_state_for`, as queryset filters ----------


def _planned(queryset: QuerySet) -> QuerySet:
    # Drafts are excluded before any date condition applies (ADS-FR-019-01), and only
    # planned records are ever upcoming or overdue (ADS-FR-034-01).
    return queryset.exclude(status=ExaminationStatus.DRAFT).filter(
        status=ExaminationStatus.PLANNED, scheduled_date__isnull=False
    )


def overdue_queryset(queryset: QuerySet, local_now: datetime) -> QuerySet:
    """Planned records whose date has passed, or whose time today has passed (§9.4)."""
    today, current_time = local_clock(local_now)
    return _planned(queryset).filter(
        Q(scheduled_date__lt=today)
        | Q(scheduled_date=today, scheduled_time__isnull=False, scheduled_time__lt=current_time)
    )


def upcoming_queryset(queryset: QuerySet, local_now: datetime) -> QuerySet:
    """Planned records that are not overdue (§9.3)."""
    today, current_time = local_clock(local_now)
    return _planned(queryset).filter(
        Q(scheduled_date__gt=today)
        | Q(scheduled_date=today, scheduled_time__isnull=True)
        | Q(scheduled_date=today, scheduled_time__gte=current_time)
    )


def past_queryset(queryset: QuerySet, local_now: datetime) -> QuerySet:
    """Completed records by completion date and cancelled or missed records by scheduled
    date, on or before the user's local date (ADS-FR-031-01, §9.2)."""
    today, _ = local_clock(local_now)
    return queryset.filter(
        Q(status=ExaminationStatus.COMPLETED, completed_date__lte=today)
        | Q(
            status__in=[ExaminationStatus.CANCELLED, ExaminationStatus.MISSED],
            scheduled_date__lte=today,
        )
    )


COLLECTION_QUERYSETS = {
    PAST: past_queryset,
    UPCOMING: upcoming_queryset,
    OVERDUE: overdue_queryset,
}
