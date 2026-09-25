from django.urls import path

from . import views

auth_patterns = [
    path("register/", views.RegisterView.as_view(), name="auth-register"),
]
