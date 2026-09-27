import re
from collections.abc import Mapping

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from config.clock import user_local_now

from .models import (
    ExaminationCategory,
    ExaminationRecord,
    ExaminationStatus,
    RecurrenceInterval,
    RecurrenceRule,
    Reminder,
)
from .recurrence_math import next_due_date
from .services import update_examination
from .time_state import COLLECTIONS, OVERDUE, UPCOMING, time_state_for
from .validators import validate_resulting_record

READ_ONLY_REJECTED = "This field is read-only."


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExaminationCategory
        fields = ["id", "name", "slug"]
        read_only_fields = fields


def local_now_from(context):
    """The requesting user's local now, computed once per request and shared."""
    if "local_now" not in context:
        context["local_now"] = user_local_now(context["request"].user)
    return context["local_now"]


class ExaminationSerializer(serializers.ModelSerializer):
    """The examination representation and its create/update input (api_contract.md §8).

    Ownership, the source occurrence, the derived time state and the audit instants
    are never accepted from a client (§10); a request that sends one is rejected.
    Every create and update validates the complete resulting record (§8.2).
    """

    NON_WRITABLE = ("user_id", "source_occurrence", "time_state", "created_at", "updated_at")
    VALIDATED_FIELDS = (
        "title",
        "status",
        "scheduled_date",
        "scheduled_time",
        "completed_date",
        "category",
    )

    user_id = serializers.IntegerField(read_only=True)
    # Both may be null (api_contract.md §8.1); allow_null puts that in the OpenAPI schema.
    category = CategorySerializer(read_only=True, allow_null=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=ExaminationCategory.objects.all(),
        allow_null=True,
        required=False,
        write_only=True,
    )
    source_occurrence = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    time_state = serializers.SerializerMethodField()

    class Meta:
        model = ExaminationRecord
        fields = [
            "id",
            "user_id",
            "category",
            "category_id",
            "title",
            "medical_specialty",
            "scheduled_date",
            "scheduled_time",
            "completed_date",
            "status",
            "location",
            "notes",
            "source_occurrence",
            "time_state",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "medical_specialty": {"required": False, "allow_null": True},
            "scheduled_date": {"required": False, "allow_null": True},
            "scheduled_time": {"required": False, "allow_null": True},
            "completed_date": {"required": False, "allow_null": True},
            "location": {"required": False, "allow_null": True},
            "notes": {"required": False, "allow_null": True},
        }

    @extend_schema_field(
        serializers.ChoiceField(choices=[UPCOMING, OVERDUE], allow_null=True, read_only=True)
    )
    def get_time_state(self, record):
        return time_state_for(record, local_now_from(self.context))

    def to_internal_value(self, data):
        rejected = {}
        if isinstance(data, Mapping):
            rejected = {field: [READ_ONLY_REJECTED] for field in self.NON_WRITABLE if field in data}
        try:
            value = super().to_internal_value(data)
        except serializers.ValidationError as error:
            if rejected and isinstance(error.detail, dict):
                raise serializers.ValidationError({**rejected, **error.detail}) from None
            raise
        if rejected:
            raise serializers.ValidationError(rejected)
        return value

    def validate(self, attrs):
        resulting = {field: getattr(self.instance, field, None) for field in self.VALIDATED_FIELDS}
        resulting.update(attrs)
        validate_resulting_record(resulting, self.context["request"].user)
        return attrs

    def update(self, instance, validated_data):
        return update_examination(instance, validated_data)


class ReminderSerializer(serializers.ModelSerializer):
    """The reminder representation (api_contract.md §14)."""

    offset_days = serializers.IntegerField(
        min_value=1, help_text="Whole days before the scheduled date; greater than zero."
    )

    class Meta:
        model = Reminder
        fields = [
            "id",
            "examination",
            "offset_days",
            "due_date",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "examination", "due_date", "created_at", "updated_at"]


class ReminderCreateSerializer(ReminderSerializer):
    """`POST .../reminder/`: an offset only; a new reminder is active."""

    class Meta(ReminderSerializer.Meta):
        read_only_fields = [*ReminderSerializer.Meta.read_only_fields, "is_active"]


class ReminderUpdateSerializer(ReminderSerializer):
    """`PATCH .../reminder/`: change the offset, disable, or re-enable."""

    offset_days = serializers.IntegerField(min_value=1, required=False)


class ExaminationListQuerySerializer(serializers.Serializer):
    """Query parameters of `GET /api/v1/examinations/` (api_contract.md §9.1).

    Every supplied value is validated; an unsupported one is a 400.
    """

    ORDERINGS = ("scheduled_date", "-scheduled_date")

    search = serializers.CharField(
        required=False, max_length=200, help_text="Case-insensitive containment on the title."
    )
    status = serializers.ChoiceField(choices=ExaminationStatus.values, required=False)
    category = serializers.PrimaryKeyRelatedField(
        queryset=ExaminationCategory.objects.all(),
        required=False,
        help_text="A category identifier.",
    )
    ordering = serializers.ChoiceField(choices=ORDERINGS, required=False)
    time_state = serializers.ChoiceField(
        choices=COLLECTIONS,
        required=False,
        help_text=(
            "A derived collection: past, upcoming or overdue. Distinct from the time_state "
            "response field, whose values are upcoming, overdue or null."
        ),
    )


class DueReminderQuerySerializer(serializers.Serializer):
    """`GET /api/v1/reminders/` query: `state=due` is the one supported view (§14.4)."""

    state = serializers.ChoiceField(choices=["due"])


class RecurrenceRuleSerializer(serializers.ModelSerializer):
    """The recurrence representation (api_contract.md §15).

    `next_due_date` is derived from the examination's current scheduled date with
    calendar-month arithmetic, and is null while there is none.
    """

    interval = serializers.ChoiceField(choices=RecurrenceInterval.values)
    next_due_date = serializers.SerializerMethodField()

    class Meta:
        model = RecurrenceRule
        fields = ["id", "examination", "interval", "next_due_date", "created_at", "updated_at"]
        read_only_fields = ["id", "examination", "created_at", "updated_at"]

    @extend_schema_field(serializers.DateField(allow_null=True, read_only=True))
    def get_next_due_date(self, rule):
        return next_due_date(rule.examination.scheduled_date, rule.interval)


class StrictDateField(serializers.DateField):
    """A calendar date written exactly as `YYYY-MM-DD` (api_contract.md §2, §17).

    Python's ISO parser also accepts forms such as `20260801`; those are rejected here.
    """

    PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    def to_internal_value(self, value):
        if not isinstance(value, str) or not self.PATTERN.match(value):
            self.fail("invalid", format="YYYY-MM-DD")
        return super().to_internal_value(value)


class CalendarQuerySerializer(serializers.Serializer):
    """`GET /api/v1/calendar/` parameters (ADS-FR-042-02): both required, start <= end."""

    start_date = StrictDateField(help_text="First date of the range, YYYY-MM-DD, inclusive.")
    end_date = StrictDateField(help_text="Last date of the range, YYYY-MM-DD, inclusive.")

    def validate(self, attrs):
        if attrs["start_date"] > attrs["end_date"]:
            raise serializers.ValidationError(
                {"start_date": ["The start date must not be later than the end date."]}
            )
        return attrs


class CalendarExaminationSerializer(ExaminationSerializer):
    """The examination subset carried by a calendar entry (api_contract.md §17)."""

    class Meta(ExaminationSerializer.Meta):
        fields = [
            "id",
            "title",
            "category",
            "scheduled_date",
            "scheduled_time",
            "completed_date",
            "status",
            "time_state",
        ]


CALENDAR_STATES = [*ExaminationStatus.values[1:], OVERDUE]


class CalendarEntrySerializer(serializers.Serializer):
    calendar_date = serializers.DateField()
    state = serializers.ChoiceField(choices=CALENDAR_STATES)
    examination = CalendarExaminationSerializer()


class StatusCountsSerializer(serializers.Serializer):
    draft = serializers.IntegerField()
    planned = serializers.IntegerField()
    completed = serializers.IntegerField()
    cancelled = serializers.IntegerField()
    missed = serializers.IntegerField()


class CategoryCountSerializer(serializers.Serializer):
    category = CategorySerializer()
    count = serializers.IntegerField()


class DashboardSerializer(serializers.Serializer):
    """`GET /api/v1/dashboard/` (api_contract.md §18)."""

    upcoming = ExaminationSerializer(many=True)
    overdue = ExaminationSerializer(many=True)
    recently_completed = ExaminationSerializer(many=True)
    status_counts = StatusCountsSerializer()
    category_counts = CategoryCountSerializer(many=True)
    uncategorized_count = serializers.IntegerField()
    overdue_count = serializers.IntegerField()
