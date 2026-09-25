"""Settings shared by every environment.

Environment-specific values live in `development.py` and `production.py`; neither
falls back to the other.
"""

from pathlib import Path

from .env import Env

env = Env()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    # ADS-SEC-001-01: authenticated access is the default for every endpoint.
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "UNAUTHENTICATED_USER": None,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Medical Tracker API",
    "DESCRIPTION": "JSON REST API for the Medical Tracker Application MVP (api_contract.md).",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    # The schema endpoint is not one of the ADS-SEC-001-01 exemptions.
    "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAuthenticated"],
}

# ADS-SEC-005-07 and ADS-SEC-005-08: the CSRF cookie is HttpOnly in every environment
# and scoped to the API. Its Secure and SameSite values are environment-specific.
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_PATH = "/api/v1/"

# ADS-SEC-005-02: credentialed requests only from the configured origins, and the
# three request headers the API contract needs.
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ("authorization", "content-type", "x-csrftoken")
CORS_URLS_REGEX = r"^/api/.*$"
