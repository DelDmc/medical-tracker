"""Recurrence next-due-date arithmetic (ADS-FR-040-01, ADS-FR-040-02).

Calendar-month arithmetic, never a fixed number of days: add one month, six months or
twelve months to the source's scheduled date, and when the target month is shorter
than the source day, use the target month's last day. 2026-01-31 plus one month is
2026-02-28; 2028-02-29 plus one year is 2029-02-28.

This is the only implementation: the recurrence representation and next-occurrence
creation both call it.
"""

import calendar
from datetime import date

from .models import RecurrenceInterval

MONTHS_PER_INTERVAL = {
    RecurrenceInterval.MONTHLY: 1,
    RecurrenceInterval.SIX_MONTHS: 6,
    RecurrenceInterval.YEARLY: 12,
}


def add_calendar_months(start: date, months: int) -> date:
    month_index = start.year * 12 + (start.month - 1) + months
    year, month = divmod(month_index, 12)
    month += 1
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(start.day, last_day))


def next_due_date(scheduled_date: date | None, interval: str) -> date | None:
    """The next occurrence's date, or `None` while the source has no scheduled date."""
    if scheduled_date is None:
        return None
    return add_calendar_months(scheduled_date, MONTHS_PER_INTERVAL[interval])
