"""Local development settings (plain HTTP on localhost)."""

import secrets

from .base import *  # noqa: F403
from .base import BASE_DIR, env
from .env import validate_origins

DEBUG = env.bool("DJANGO_DEBUG", default=True)

# Secrets are never committed (ADS-SEC-004-01). Without a value in the environment a
# random per-process key is used, so sessions do not survive a server restart.
SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="") or secrets.token_urlsafe(50)
JWT_SIGNING_KEY = env.str("JWT_SIGNING_KEY", default="") or secrets.token_urlsafe(50)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "[::1]"])

DATABASES = {
    "default": env.database_url(
        "DATABASE_URL",
        default={"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"},
    )
}

FRONTEND_ORIGINS = validate_origins(
    env.list("FRONTEND_ORIGINS", default=["http://localhost:5173"]), name="FRONTEND_ORIGINS"
)
CORS_ALLOWED_ORIGINS = FRONTEND_ORIGINS
CSRF_TRUSTED_ORIGINS = FRONTEND_ORIGINS

# ADS-SEC-005-08: local HTTP development uses SameSite=Lax without Secure.
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = "Lax"

# ADS-SEC-005-04: the refresh-token cookie, likewise.
REFRESH_COOKIE_SECURE = False
REFRESH_COOKIE_SAMESITE = "Lax"

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
