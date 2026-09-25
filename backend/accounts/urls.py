from django.urls import path

from . import views

auth_patterns = [
    path("register/", views.RegisterView.as_view(), name="auth-register"),
    path("csrf/", views.CsrfBootstrapView.as_view(), name="auth-csrf"),
    path("login/", views.LoginView.as_view(), name="auth-login"),
    path("refresh/", views.RefreshView.as_view(), name="auth-refresh"),
    path("logout/", views.LogoutView.as_view(), name="auth-logout"),
]
