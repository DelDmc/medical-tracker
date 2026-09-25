from django.urls import path

from . import views

category_patterns = [
    path("", views.CategoryListView.as_view(), name="category-list"),
]

examination_patterns = [
    path("", views.ExaminationListCreateView.as_view(), name="examination-list"),
    path("<int:pk>/", views.ExaminationDetailView.as_view(), name="examination-detail"),
    path("<int:pk>/reminder/", views.ReminderView.as_view(), name="examination-reminder"),
]
