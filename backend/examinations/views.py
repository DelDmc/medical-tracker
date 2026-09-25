from rest_framework import generics

from .models import ExaminationCategory
from .querysets import OwnedExaminationMixin
from .serializers import CategorySerializer, ExaminationSerializer


class CategoryListView(generics.ListAPIView):
    """`GET /api/v1/categories/` — read-only; no create, update or delete route exists."""

    queryset = ExaminationCategory.objects.all()
    serializer_class = CategorySerializer


class ExaminationListCreateView(OwnedExaminationMixin, generics.ListCreateAPIView):
    """`GET` / `POST /api/v1/examinations/` — only the caller's records; a JSON array."""

    serializer_class = ExaminationSerializer

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
