"""Production settings.

Every mandatory value is read without a default, so a missing one raises
`ImproperlyConfigured` at import time and the process never starts (ADS-TECH-005-01).
Nothing here imports or falls back to the development settings.
"""

from .base import *  # noqa: F403
from .base import env
from .env import validate_origins

# ADS-TECH-005-01: unconditional; not read from the environment.
DEBUG = False

SECRET_KEY = env.str("DJANGO_SECRET_KEY")
JWT_SIGNING_KEY = env.str("JWT_SIGNING_KEY")

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")

DATABASES = {"default": env.database_url("DATABASE_URL")}

# ADS-SEC-005-01 and ADS-SEC-005-03: explicit origins only, never a wildcard.
FRONTEND_ORIGINS = validate_origins(env.list("FRONTEND_ORIGINS"), name="FRONTEND_ORIGINS")
CORS_ALLOWED_ORIGINS = FRONTEND_ORIGINS
CSRF_TRUSTED_ORIGINS = FRONTEND_ORIGINS

# ADS-SEC-005-08: the frontend and backend are separate HTTPS origins.
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True

# ADS-TECH-006-01: trust only the platform's HTTPS header, and redirect plain HTTP.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)

# Shared across worker processes so per-IP rate limits hold for the whole service.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache",
    }
}
