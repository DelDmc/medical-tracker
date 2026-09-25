from django.db.models import Case, IntegerField, Value, When
from drf_spectacular.utils import extend_schema
from rest_framework import generics

from .models import ExaminationCategory
from .querysets import OwnedExaminationMixin
from .serializers import (
    CategorySerializer,
    ExaminationListQuerySerializer,
    ExaminationSerializer,
)


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

    The list accepts `search`, `status`, `category` and `ordering`; `status` and
    `category` combine with AND semantics (ADS-FR-028-01 … ADS-FR-030-01).
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
