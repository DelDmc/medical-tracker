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

from .models import ExaminationStatus

UPCOMING = "upcoming"
OVERDUE = "overdue"


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
