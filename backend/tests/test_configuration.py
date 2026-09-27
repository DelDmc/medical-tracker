"""Configuration, health-check and settings-level security tests (Slice 0)."""

import pytest
from django.core.exceptions import ImproperlyConfigured

from tests.helpers import PRODUCTION_ENV

DEVELOPMENT = "config.settings.development"
PRODUCTION = "config.settings.production"


def test_tc_tech_003_01_development_env_values_apply_development_settings(settings_env):
    """TC-TECH-003-01 — Development environment values apply development settings."""
    development = settings_env(
        DEVELOPMENT,
        {
            "DJANGO_DEBUG": "true",
            "DJANGO_SECRET_KEY": "development-signing-value",  # pragma: allowlist secret
            "JWT_SIGNING_KEY": "development-jwt-value",  # pragma: allowlist secret
            "DJANGO_ALLOWED_HOSTS": "localhost,dev.example.test",
            "FRONTEND_ORIGINS": "http://localhost:5173,http://localhost:4173",
        },
    )

    assert development.DEBUG is True
    assert development.SECRET_KEY == "development-signing-value"  # pragma: allowlist secret
    assert development.JWT_SIGNING_KEY == "development-jwt-value"  # pragma: allowlist secret
    assert development.ALLOWED_HOSTS == ["localhost", "dev.example.test"]
    assert development.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3"
    assert development.CORS_ALLOWED_ORIGINS == ["http://localhost:5173", "http://localhost:4173"]
    assert development.CSRF_TRUSTED_ORIGINS == development.CORS_ALLOWED_ORIGINS
    assert development.CSRF_COOKIE_SECURE is False
    assert development.CSRF_COOKIE_SAMESITE == "Lax"
    assert not hasattr(development, "SECURE_PROXY_SSL_HEADER")


def test_tc_tech_003_02_production_env_values_apply_production_settings(settings_env):
    """TC-TECH-003-02 — Production environment values apply production settings."""
    production = settings_env(PRODUCTION, PRODUCTION_ENV)

    assert production.DEBUG is False
    assert production.SECRET_KEY == PRODUCTION_ENV["DJANGO_SECRET_KEY"]
    assert production.JWT_SIGNING_KEY == PRODUCTION_ENV["JWT_SIGNING_KEY"]
    assert production.ALLOWED_HOSTS == ["api.example.com"]
    database = production.DATABASES["default"]
    assert database["ENGINE"] == "django.db.backends.postgresql"
    assert (database["NAME"], database["USER"], database["HOST"], database["PORT"]) == (
        "tracker",
        "tracker",
        "db.example.com",
        "5432",
    )
    assert database["OPTIONS"] == {"sslmode": "require"}
    assert production.CORS_ALLOWED_ORIGINS == ["https://app.example.com"]
    assert production.CSRF_TRUSTED_ORIGINS == ["https://app.example.com"]
    assert production.CSRF_COOKIE_SECURE is True
    assert production.CSRF_COOKIE_SAMESITE == "None"
    assert production.SECURE_PROXY_SSL_HEADER == ("HTTP_X_FORWARDED_PROTO", "https")
    assert production.SECURE_SSL_REDIRECT is True


def test_tc_tech_003_03_missing_required_production_value_fails_startup(settings_env):
    """TC-TECH-003-03 — A missing required production value fails startup."""
    for omitted in PRODUCTION_ENV:
        environ = {name: value for name, value in PRODUCTION_ENV.items() if name != omitted}
        with pytest.raises(ImproperlyConfigured, match=omitted):
            settings_env(PRODUCTION, environ)

        blank = {**PRODUCTION_ENV, omitted: "   "}
        with pytest.raises(ImproperlyConfigured, match=omitted):
            settings_env(PRODUCTION, blank)


def test_tc_tech_004_01_health_check_returns_minimal_successful_response(api_client):
    """TC-TECH-004-01 — The health-check endpoint returns a minimal successful response."""
    response = api_client.get("/api/v1/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_tc_tech_005_01_production_settings_cannot_enable_debug_by_omission(settings_env):
    """TC-TECH-005-01 — Production settings cannot enable debug mode by omission."""
    production = settings_env(PRODUCTION, PRODUCTION_ENV)
    assert production.DEBUG is False

    # Not even an explicit development-style override reaches production.
    production = settings_env(PRODUCTION, {**PRODUCTION_ENV, "DJANGO_DEBUG": "true"})
    assert production.DEBUG is False


def test_tc_sec_001_11_health_check_does_not_require_a_bearer_token(api_client):
    """TC-SEC-001-11 — Health check does not require a bearer token."""
    response = api_client.get("/api/v1/health/")

    assert response.status_code not in (401, 403)
    assert response.status_code == 200


def test_tc_sec_005_03_production_cors_configuration_contains_no_wildcard(settings_env):
    """TC-SEC-005-03 — Production CORS configuration contains no wildcard origin."""
    production = settings_env(
        PRODUCTION,
        {
            **PRODUCTION_ENV,
            "FRONTEND_ORIGINS": "https://app.example.com,https://preview.example.com",
        },
    )
    assert production.CORS_ALLOWED_ORIGINS == [
        "https://app.example.com",
        "https://preview.example.com",
    ]
    assert not any("*" in origin for origin in production.CORS_ALLOWED_ORIGINS)
    assert not getattr(production, "CORS_ALLOW_ALL_ORIGINS", False)
    assert not getattr(production, "CORS_ORIGIN_ALLOW_ALL", False)

    for wildcard in ("*", "https://*.example.com", "https://app.example.com,*"):
        with pytest.raises(ImproperlyConfigured, match="wildcard"):
            settings_env(PRODUCTION, {**PRODUCTION_ENV, "FRONTEND_ORIGINS": wildcard})
