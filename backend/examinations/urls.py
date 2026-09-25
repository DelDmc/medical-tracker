from django.urls import path

from . import views

category_patterns = [
    path("", views.CategoryListView.as_view(), name="category-list"),
]

examination_patterns = [
    path("", views.ExaminationListCreateView.as_view(), name="examination-list"),
]
