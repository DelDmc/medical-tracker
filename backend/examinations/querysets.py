"""Owner-scoped lookups (ADS-SEC-002-01, ADS-SEC-006-01).

Every examination, reminder and recurrence view resolves examinations only from the
authenticated user's own queryset. A record that does not exist and a record that
belongs to someone else are therefore the same miss, answered by one code path with
the same `404 {"detail": "Not found."}`.
"""

from rest_framework.exceptions import NotFound

from .models import ExaminationRecord


class OwnedExaminationMixin:
    examination_lookup_kwarg = "pk"

    def get_queryset(self):
        return ExaminationRecord.objects.filter(user=self.request.user).select_related("category")

    def get_examination(self) -> ExaminationRecord:
        try:
            return self.get_queryset().get(pk=self.kwargs[self.examination_lookup_kwarg])
        except (ExaminationRecord.DoesNotExist, ValueError, TypeError):
            raise NotFound() from None

    def get_object(self):
        examination = self.get_examination()
        self.check_object_permissions(self.request, examination)
        return examination
