from django.db import IntegrityError, transaction
from django.db.models import Case, IntegerField, Value, When
from drf_spectacular.utils import extend_schema
from rest_framework import generics, serializers, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from config.clock import user_local_date

from .models import ExaminationCategory, Reminder
from .querysets import OwnedExaminationMixin
from .serializers import (
    CategorySerializer,
    DueReminderQuerySerializer,
    ExaminationListQuerySerializer,
    ExaminationSerializer,
    RecurrenceRuleSerializer,
    ReminderCreateSerializer,
    ReminderSerializer,
    ReminderUpdateSerializer,
)
from .services import get_recurrence_rule, get_reminder
from .time_state import COLLECTION_QUERYSETS
from .validators import (
    RECURRENCE_REQUIRES_PLANNED,
    REMINDER_REQUIRES_PLANNED,
    require_planned,
)

REMINDER_EXISTS = "This examination already has a reminder."
RECURRENCE_EXISTS = "This examination already has a recurrence rule."


class CategoryListView(generics.ListAPIView):
    """`GET /api/v1/categories/` — read-only; no create, update or delete route exists."""

    queryset = ExaminationCategory.objects.all()
    serializer_class = CategorySerializer


def order_by_scheduled_date(queryset, ordering):
    """Order by scheduled date with undated records last in *both* directions.

    Null placement is spelled out rather than left to the database, because SQLite and
    PostgreSQL disagree about it (ADS-FR-030-01). Equal dates fall back to the
    identifier, so ties come back in the same order every time.
    """
    undated_last = Case(
        When(scheduled_date__isnull=True, then=Value(1)),
        default=Value(0),
        output_field=IntegerField(),
    )
    return queryset.annotate(undated=undated_last).order_by("undated", ordering, "id")


class ExaminationListCreateView(OwnedExaminationMixin, generics.ListCreateAPIView):
    """`GET` / `POST /api/v1/examinations/` — only the caller's records; a JSON array.

    The list accepts `search`, `status`, `category`, `ordering` and `time_state`; all
    supplied filters apply together (ADS-FR-028-01 … ADS-FR-032-01). `time_state`
    selects the past, upcoming or overdue collection through examinations/time_state.py.
    """

    serializer_class = ExaminationSerializer

    def filter_queryset(self, queryset):
        params = ExaminationListQuerySerializer(data=self.request.query_params)
        params.is_valid(raise_exception=True)
        filters = params.validated_data
        if search := filters.get("search"):
            queryset = queryset.filter(title__icontains=search)
        if status := filters.get("status"):
            queryset = queryset.filter(status=status)
        if category := filters.get("category"):
            queryset = queryset.filter(category=category)
        if collection := filters.get("time_state"):
            queryset = COLLECTION_QUERYSETS[collection](queryset, self.get_local_now())
        if ordering := filters.get("ordering"):
            queryset = order_by_scheduled_date(queryset, ordering)
        return queryset

    @extend_schema(parameters=[ExaminationListQuerySerializer])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Ownership is assigned here, never taken from the request (ADS-SEC-002-01).
        serializer.save(user=self.request.user)


class ExaminationDetailView(OwnedExaminationMixin, generics.RetrieveUpdateDestroyAPIView):
    """`GET` / `PATCH` / `DELETE /api/v1/examinations/{id}/`.

    The record is looked up only among the caller's own examinations, so a missing
    record and another user's record get the same 404 (ADS-SEC-006-01). `PATCH` is
    partial, but the complete resulting record is validated (ADS-FR-022-01); `PUT` is
    not offered (api_contract.md §12). Deleting cascades to the reminder and the
    recurrence rule and nulls `source_occurrence` on generated occurrences
    (ADS-FR-023-01, ADS-FR-023-02).
    """

    serializer_class = ExaminationSerializer
    http_method_names = ["get", "patch", "delete", "head", "options"]


class ReminderView(OwnedExaminationMixin, APIView):
    """`GET` / `POST` / `PATCH /api/v1/examinations/{id}/reminder/` (api_contract.md §14).

    The examination is resolved only among the caller's own, so another user's
    examination and a missing one — or a missing reminder — are the same 404.
    Creation, offset changes and reactivation need a planned examination; disabling
    does not (ADS-FR-035-02).
    """

    def get_reminder_or_404(self, examination):
        reminder = get_reminder(examination)
        if reminder is None:
            raise NotFound()
        return reminder

    @extend_schema(responses={200: ReminderSerializer})
    def get(self, request, pk):
        reminder = self.get_reminder_or_404(self.get_examination())
        return Response(ReminderSerializer(reminder).data)

    @extend_schema(request=ReminderCreateSerializer, responses={201: ReminderSerializer})
    def post(self, request, pk):
        examination = self.get_examination()
        if get_reminder(examination) is not None:
            raise serializers.ValidationError({"non_field_errors": [REMINDER_EXISTS]})
        serializer = ReminderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        require_planned(examination, REMINDER_REQUIRES_PLANNED)
        try:
            with transaction.atomic():
                reminder = serializer.save(examination=examination, is_active=True)
        except IntegrityError:
            raise serializers.ValidationError({"non_field_errors": [REMINDER_EXISTS]}) from None
        return Response(ReminderSerializer(reminder).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=ReminderUpdateSerializer, responses={200: ReminderSerializer})
    def patch(self, request, pk):
        examination = self.get_examination()
        reminder = self.get_reminder_or_404(examination)
        serializer = ReminderUpdateSerializer(reminder, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        changes = serializer.validated_data
        if "offset_days" in changes or changes.get("is_active") is True:
            require_planned(examination, REMINDER_REQUIRES_PLANNED)
        reminder = serializer.save()
        return Response(ReminderSerializer(reminder).data)


class DueReminderListView(generics.ListAPIView):
    """`GET /api/v1/reminders/?state=due` (ADS-FR-037-01, domain_model.md §6.6).

    Active reminders due on or before the user's current local date, on the user's own
    examinations only. The backend is the single definition of "due".
    """

    serializer_class = ReminderSerializer

    def get_queryset(self):
        params = DueReminderQuerySerializer(data=self.request.query_params)
        params.is_valid(raise_exception=True)
        user = self.request.user
        return (
            Reminder.objects.filter(
                examination__user=user, is_active=True, due_date__lte=user_local_date(user)
            )
            .select_related("examination")
            .order_by("due_date", "id")
        )

    @extend_schema(parameters=[DueReminderQuerySerializer])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RecurrenceView(OwnedExaminationMixin, APIView):
    """`GET` / `POST` / `PATCH /api/v1/examinations/{id}/recurrence/` (api_contract.md §15).

    Resolved inside the caller's own examinations (a missing examination or rule is the
    same 404). Creation and updates need a planned examination with a scheduled date
    (ADS-FR-018-01, ADS-FR-039-01); a retained rule stays readable in any status and
    is never changed by a status change (ADS-FR-039-02).
    """

    def get_rule_or_404(self, examination):
        rule = get_recurrence_rule(examination)
        if rule is None:
            raise NotFound()
        return rule

    @extend_schema(responses={200: RecurrenceRuleSerializer})
    def get(self, request, pk):
        rule = self.get_rule_or_404(self.get_examination())
        return Response(RecurrenceRuleSerializer(rule).data)

    @extend_schema(request=RecurrenceRuleSerializer, responses={201: RecurrenceRuleSerializer})
    def post(self, request, pk):
        examination = self.get_examination()
        if get_recurrence_rule(examination) is not None:
            raise serializers.ValidationError({"non_field_errors": [RECURRENCE_EXISTS]})
        serializer = RecurrenceRuleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        require_planned(examination, RECURRENCE_REQUIRES_PLANNED)
        try:
            with transaction.atomic():
                rule = serializer.save(examination=examination)
        except IntegrityError:
            raise serializers.ValidationError({"non_field_errors": [RECURRENCE_EXISTS]}) from None
        return Response(RecurrenceRuleSerializer(rule).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=RecurrenceRuleSerializer, responses={200: RecurrenceRuleSerializer})
    def patch(self, request, pk):
        examination = self.get_examination()
        rule = self.get_rule_or_404(examination)
        serializer = RecurrenceRuleSerializer(rule, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        require_planned(examination, RECURRENCE_REQUIRES_PLANNED)
        rule = serializer.save()
        return Response(RecurrenceRuleSerializer(rule).data)
