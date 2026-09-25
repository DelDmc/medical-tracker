"""The dashboard's collections and counts (api_contract.md §18)."""

from datetime import datetime, timedelta

from django.db.models import Count, F, Q, QuerySet

from .models import ExaminationCategory, ExaminationStatus
from .time_state import local_clock, overdue_queryset, upcoming_queryset

RECENTLY_COMPLETED_DAYS = 30
RECENTLY_COMPLETED_LIMIT = 5


def _by_schedule(queryset: QuerySet) -> QuerySet:
    # Explicit null placement, not the database default (IMPLEMENTATION_PLAN.md R6).
    return queryset.order_by("scheduled_date", F("scheduled_time").asc(nulls_last=True), "id")


def dashboard_data(owned: QuerySet, user, local_now: datetime) -> dict:
    """Everything the dashboard shows, computed for one instant of the user's clock.

    `upcoming` and `overdue` are the shared collection queries (ADS-FR-044-01), and
    `overdue_count` counts that same overdue result (ADS-FR-047-01).
    """
    today, _ = local_clock(local_now)
    upcoming = list(_by_schedule(upcoming_queryset(owned, local_now)))
    overdue = list(_by_schedule(overdue_queryset(owned, local_now)))

    # Filter, then order, then limit (ADS-FR-044-02 … 044-04). The upper bound is kept
    # defensively although validation already rejects future completion dates.
    window_start = today - timedelta(days=RECENTLY_COMPLETED_DAYS - 1)
    recently_completed = list(
        owned.filter(
            status=ExaminationStatus.COMPLETED,
            completed_date__gte=window_start,
            completed_date__lte=today,
        ).order_by("-completed_date", "-id")[:RECENTLY_COMPLETED_LIMIT]
    )

    counted = dict(owned.order_by().values_list("status").annotate(total=Count("id")))
    status_counts = {status: counted.get(status, 0) for status in ExaminationStatus.values}

    category_counts = [
        {"category": category, "count": category.total}
        for category in ExaminationCategory.objects.annotate(
            total=Count("examinations", filter=Q(examinations__user=user))
        ).order_by("id")
    ]

    return {
        "upcoming": upcoming,
        "overdue": overdue,
        "recently_completed": recently_completed,
        "status_counts": status_counts,
        "category_counts": category_counts,
        "uncategorized_count": owned.filter(category__isnull=True).count(),
        "overdue_count": len(overdue),
    }
