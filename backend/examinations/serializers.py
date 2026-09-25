from collections.abc import Mapping

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from config.clock import user_local_now

from .models import ExaminationCategory, ExaminationRecord
from .time_state import OVERDUE, UPCOMING, time_state_for
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
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=ExaminationCategory.objects.all(),
        allow_null=True,
        required=False,
        write_only=True,
    )
    source_occurrence = serializers.PrimaryKeyRelatedField(read_only=True)
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
