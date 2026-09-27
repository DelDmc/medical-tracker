from django.urls import path

from . import views

category_patterns = [
    path("", views.CategoryListView.as_view(), name="category-list"),
]

examination_patterns = [
    path("", views.ExaminationListCreateView.as_view(), name="examination-list"),
    path("<int:pk>/", views.ExaminationDetailView.as_view(), name="examination-detail"),
    path("<int:pk>/reminder/", views.ReminderView.as_view(), name="examination-reminder"),
    path("<int:pk>/recurrence/", views.RecurrenceView.as_view(), name="examination-recurrence"),
    path(
        "<int:pk>/next-occurrence/",
        views.NextOccurrenceView.as_view(),
        name="examination-next-occurrence",
    ),
]

reminder_patterns = [
    path("", views.DueReminderListView.as_view(), name="reminder-list"),
]

calendar_patterns = [
    path("", views.CalendarView.as_view(), name="calendar"),
]

dashboard_patterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
]
