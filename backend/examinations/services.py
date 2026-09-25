"""Examination updates and their side effects."""

from django.db import transaction

from .models import ExaminationRecord, ExaminationStatus, Reminder


def get_reminder(examination: ExaminationRecord) -> Reminder | None:
    try:
        return examination.reminder
    except Reminder.DoesNotExist:
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
