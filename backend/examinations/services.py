"""Examination updates and their side effects."""

from django.db import transaction

from .models import ExaminationRecord, Reminder


def get_reminder(examination: ExaminationRecord) -> Reminder | None:
    try:
        return examination.reminder
    except Reminder.DoesNotExist:
        return None


@transaction.atomic
def update_examination(examination: ExaminationRecord, changes: dict) -> ExaminationRecord:
    """Apply validated changes and keep the attached reminder consistent, atomically.

    Re-saving the reminder recalculates its due date from the (possibly new) scheduled
    date (ADS-FR-036-01).
    """
    for field, value in changes.items():
        setattr(examination, field, value)
    examination.save()
    reminder = get_reminder(examination)
    if reminder is not None:
        reminder.save()
    return examination
