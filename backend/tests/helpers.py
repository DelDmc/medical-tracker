"""Shared request helpers for the API tests."""

import jwt

from tests.conftest import DEFAULT_PASSWORD, load_settings_module

CSRF_URL = "/api/v1/auth/csrf/"
LOGIN_URL = "/api/v1/auth/login/"
REFRESH_URL = "/api/v1/auth/refresh/"
LOGOUT_URL = "/api/v1/auth/logout/"

PRODUCTION_ENV = {
    "DJANGO_SECRET_KEY": "production-signing-value-for-tests-only",  # pragma: allowlist secret
    "JWT_SIGNING_KEY": "production-jwt-value-for-tests-only",  # pragma: allowlist secret
    "DJANGO_ALLOWED_HOSTS": "api.example.com",
    "DATABASE_URL": "postgres://tracker@db.example.com:5432/tracker?sslmode=require",
    "FRONTEND_ORIGINS": "https://app.example.com",
}

COOKIE_SETTINGS = (
    "CSRF_COOKIE_HTTPONLY",
    "CSRF_COOKIE_PATH",
    "CSRF_COOKIE_SECURE",
    "CSRF_COOKIE_SAMESITE",
    "REFRESH_COOKIE_SECURE",
    "REFRESH_COOKIE_SAMESITE",
    "CSRF_COOKIE_PARTITIONED",
    "REFRESH_COOKIE_PARTITIONED",
)


def use_cookie_settings_of(settings, module_name, environ=None):
    """Apply a settings module's cookie configuration to the running test settings."""
    module = load_settings_module(module_name, environ or PRODUCTION_ENV)
    for name in COOKIE_SETTINGS:
        setattr(settings, name, getattr(module, name))
    return module


def bootstrap_csrf(client) -> str:
    response = client.get(CSRF_URL)
    assert response.status_code == 200
    return response.json()["csrf_token"]


def login(client, email, password=DEFAULT_PASSWORD, csrf_token=None):
    csrf_token = csrf_token or bootstrap_csrf(client)
    return client.post(
        LOGIN_URL,
        {"email": email, "password": password},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )


def refresh(client, csrf_token=None):
    csrf_token = csrf_token or bootstrap_csrf(client)
    return client.post(REFRESH_URL, HTTP_X_CSRFTOKEN=csrf_token)


def logout(client, csrf_token=None):
    csrf_token = csrf_token or bootstrap_csrf(client)
    return client.post(LOGOUT_URL, HTTP_X_CSRFTOKEN=csrf_token)


def refresh_cookie(client_or_response):
    morsel = client_or_response.cookies.get("refresh_token")
    return morsel.value if morsel is not None else None


def set_refresh_cookie(client, token):
    client.cookies["refresh_token"] = token


def authenticate_as(client, user):
    """Log `user` in through the API and send its access token on every request."""
    response = login(client, user.email)
    assert response.status_code == 200, response.content
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['access_token']}")
    return response.json()["access_token"]


def decode_unverified(token):
    return jwt.get_unverified_header(token), jwt.decode(token, options={"verify_signature": False})
