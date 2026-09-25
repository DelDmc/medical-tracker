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
