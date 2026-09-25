from django.conf import settings
from django.db import models
from django.db.models import Q

from config import clock


class ExaminationCategory(models.Model):
    """A fixed, system-defined category (domain_model.md §3.2). Seeded, never edited.

    An examination without a category is "Uncategorized": that is a presentation
    fallback for `null`, not a row here.
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ["id"]
        verbose_name_plural = "examination categories"

    def __str__(self):
        return self.name


class TimestampedModel(models.Model):
    """Timezone-aware audit instants (ADS-TECH-002-01), read from the clock service."""

    created_at = models.DateTimeField(default=clock.now, editable=False)
    updated_at = models.DateTimeField(default=clock.now, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        now = clock.now()
        if self._state.adding:
            self.created_at = now
        self.updated_at = now
        if kwargs.get("update_fields") is not None:
            kwargs["update_fields"] = {*kwargs["update_fields"], "updated_at"}
        super().save(*args, **kwargs)


class ExaminationStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PLANNED = "planned", "Planned"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    MISSED = "missed", "Missed"


class ExaminationRecord(TimestampedModel):
    """A user-owned examination or appointment (domain_model.md §3.3).

    The field set is the approved whitelist (ADS-PRV-001-01): adding a stored field
    needs an approved requirements and design change first. `overdue` is never stored;
    it is derived from these fields and the user's current local time
    (examinations/time_state.py).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="examinations"
    )
    category = models.ForeignKey(
        ExaminationCategory,
        null=True,
        blank=True,
        # Categories are seed data and are never deleted.
        on_delete=models.PROTECT,
        related_name="examinations",
    )
    title = models.CharField(max_length=200)
    # The API represents an absent optional text value as null (api_contract.md §8.1),
    # so these text columns are nullable on purpose.
    medical_specialty = models.CharField(max_length=200, null=True, blank=True)  # noqa: DJ001
    # Calendar values: a date and a separate optional local time (ADS-TECH-002-01).
    scheduled_date = models.DateField(null=True, blank=True)
    scheduled_time = models.TimeField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=ExaminationStatus.choices)
    location = models.CharField(max_length=255, null=True, blank=True)  # noqa: DJ001
    notes = models.TextField(null=True, blank=True)  # noqa: DJ001
    source_occurrence = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        # Deleting a source leaves generated occurrences in place (ADS-FR-023-02).
        on_delete=models.SET_NULL,
        related_name="generated_occurrences",
    )

    class Meta:
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=ExaminationStatus.values),
                name="examination_status_valid",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "scheduled_date"]),
        ]

    def __str__(self):
        return self.title


class Reminder(TimestampedModel):
    """The single in-application reminder of an examination (domain_model.md §3.4).

    Ownership is the examination's. `due_date = scheduled_date - offset_days`, null
    without a scheduled date.
    """

    examination = models.OneToOneField(
        ExaminationRecord, on_delete=models.CASCADE, related_name="reminder"
    )
    offset_days = models.PositiveIntegerField()
    due_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(offset_days__gte=1), name="reminder_offset_positive"
            ),
        ]

    def __str__(self):
        return f"Reminder {self.offset_days} days before {self.examination}"


class RecurrenceInterval(models.TextChoices):
    MONTHLY = "monthly", "Monthly"
    SIX_MONTHS = "six_months", "Every six months"
    YEARLY = "yearly", "Yearly"


class RecurrenceRule(TimestampedModel):
    """The optional recurrence of an examination (domain_model.md §3.5)."""

    examination = models.OneToOneField(
        ExaminationRecord, on_delete=models.CASCADE, related_name="recurrence_rule"
    )
    interval = models.CharField(max_length=16, choices=RecurrenceInterval.choices)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(interval__in=RecurrenceInterval.values),
                name="recurrence_interval_valid",
            ),
        ]

    def __str__(self):
        return f"{self.get_interval_display()} recurrence of {self.examination}"
