"""Business-rule validation for examinations (ADS-FR-014-01, ADS-FR-014-02).

`validate_resulting_record` always receives the complete record a request would
produce — for a PATCH, the stored instance merged with the submitted changes — never
the submitted diff alone (api_contract.md §8.2).
"""

from collections.abc import Mapping

from rest_framework import serializers

from config.clock import user_local_date

from .models import ExaminationStatus

REQUIRES_SCHEDULED_DATE = {
    ExaminationStatus.PLANNED,
    ExaminationStatus.CANCELLED,
    ExaminationStatus.MISSED,
}
SCHEDULED_DATE_REQUIRED = "A scheduled date is required for this status."
COMPLETED_DATE_REQUIRED = "A completion date is required for this status."
COMPLETED_DATE_IN_FUTURE = "The completion date cannot be later than today."
REMINDER_REQUIRES_PLANNED = "Reminders can be set up only while the examination is planned."
RECURRENCE_REQUIRES_PLANNED = "Recurrence can be set up only while the examination is planned."


def validate_resulting_record(record: Mapping, user) -> None:
    """Apply the status-dependent required-field rules to a complete record."""
    errors = {}
    title = record.get("title")
    if title is None or not str(title).strip():
        errors["title"] = ["This field is required."]

    status = record.get("status")
    if status in REQUIRES_SCHEDULED_DATE and record.get("scheduled_date") is None:
        errors["scheduled_date"] = [SCHEDULED_DATE_REQUIRED]
    if status == ExaminationStatus.COMPLETED:
        completed_date = record.get("completed_date")
        if completed_date is None:
            errors["completed_date"] = [COMPLETED_DATE_REQUIRED]
        elif completed_date > user_local_date(user):
            errors["completed_date"] = [COMPLETED_DATE_IN_FUTURE]

    if errors:
        raise serializers.ValidationError(errors)


def require_planned(examination, message: str) -> None:
    """Reject a reminder or recurrence change unless the examination is planned.

    A business-rule error, reported under `non_field_errors` (api_contract.md §3.4).
    Used for reminder creation, offset updates and reactivation (ADS-FR-017-01,
    ADS-FR-035-02) and for recurrence creation and updates (ADS-FR-018-01,
    ADS-FR-039-01).
    """
    if examination.status != ExaminationStatus.PLANNED:
        raise serializers.ValidationError({"non_field_errors": [message]})
