"""Examination updates and their side effects."""

from django.db import transaction

from .models import ExaminationRecord, ExaminationStatus, RecurrenceRule, Reminder
from .recurrence_math import next_due_date


def get_reminder(examination: ExaminationRecord) -> Reminder | None:
    try:
        return examination.reminder
    except Reminder.DoesNotExist:
        return None


def get_recurrence_rule(examination: ExaminationRecord) -> RecurrenceRule | None:
    try:
        return examination.recurrence_rule
    except RecurrenceRule.DoesNotExist:
        return None


@transaction.atomic
def update_examination(examination: ExaminationRecord, changes: dict) -> ExaminationRecord:
    """Apply validated changes and keep the attached reminder consistent, atomically.

    - Re-saving the reminder recalculates its due date from the (possibly new)
      scheduled date (ADS-FR-036-01).
    - Leaving `planned` for any other status deactivates the reminder in this same
      transaction (ADS-FR-038-01). Returning to `planned` deliberately does not
      reactivate it; the user turns it back on explicitly.
    - The recurrence rule is untouched by any status change (ADS-FR-039-02).
    """
    left_planned = (
        examination.status == ExaminationStatus.PLANNED
        and changes.get("status", examination.status) != ExaminationStatus.PLANNED
    )
    for field, value in changes.items():
        setattr(examination, field, value)
    examination.save()
    reminder = get_reminder(examination)
    if reminder is not None:
        if left_planned:
            reminder.is_active = False
        reminder.save()
    return examination


class NextOccurrenceError(Exception):
    """The source cannot produce a next occurrence; the message says why."""


NOT_FROM_DRAFT = "A draft cannot be the source of a next occurrence."
NEEDS_SCHEDULED_DATE = "The examination needs a scheduled date to calculate the next occurrence."
NEEDS_RECURRENCE = "The examination has no recurrence rule."


def create_next_occurrence(source: ExaminationRecord) -> tuple[ExaminationRecord, bool]:
    """Create the one next occurrence of `source`, or return the one that exists.

    Returns `(occurrence, created)`. The idempotency key is the pair (source,
    calculated due date): a repeat finds the occurrence already generated for that
    date (ADS-FR-041-01, ADS-FR-041-03), while a source whose date later changes can
    legitimately produce a different one. The copied and emptied fields follow
    ADS-FR-041-04; no reminder or recurrence rule is created for the occurrence.
    """
    if source.status == ExaminationStatus.DRAFT:
        raise NextOccurrenceError(NOT_FROM_DRAFT)
    if source.scheduled_date is None:
        raise NextOccurrenceError(NEEDS_SCHEDULED_DATE)
    rule = get_recurrence_rule(source)
    if rule is None:
        raise NextOccurrenceError(NEEDS_RECURRENCE)
    due_date = next_due_date(source.scheduled_date, rule.interval)

    with transaction.atomic():
        # Lock the source so concurrent requests for it run one after the other and
        # the second sees the first one's occurrence.
        ExaminationRecord.objects.select_for_update().get(pk=source.pk)
        existing = (
            ExaminationRecord.objects.filter(source_occurrence=source, scheduled_date=due_date)
            .order_by("id")
            .first()
        )
        if existing is not None:
            return existing, False
        occurrence = ExaminationRecord.objects.create(
            user=source.user,
            title=source.title,
            category=source.category,
            medical_specialty=source.medical_specialty,
            scheduled_time=source.scheduled_time,
            location=source.location,
            status=ExaminationStatus.PLANNED,
            scheduled_date=due_date,
            source_occurrence=source,
            notes=None,
            completed_date=None,
        )
    return occurrence, True
