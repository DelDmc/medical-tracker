"""Typed environment-variable reader for the settings modules (ADS-TECH-003-01).

Every value the settings layer takes from the environment goes through `Env`, which
parses it into an explicit Python type. A variable read without a default is
mandatory: when it is absent or blank, `ImproperlyConfigured` is raised at import
time instead of falling back to any default (ADS-TECH-005-01).
"""

import os
from collections.abc import Mapping
from urllib.parse import parse_qsl, unquote, urlsplit

from django.core.exceptions import ImproperlyConfigured

_MISSING = object()
_TRUE = frozenset({"1", "true", "yes", "on"})
_FALSE = frozenset({"0", "false", "no", "off"})


class Env:
    def __init__(self, environ: Mapping[str, str] | None = None):
        self._environ = os.environ if environ is None else environ

    def _raw(self, name, default):
        value = self._environ.get(name)
        if value is None or not value.strip():
            if default is _MISSING:
                raise ImproperlyConfigured(f"The {name} environment variable is required.")
            return _MISSING
        return value.strip()

    def str(self, name: str, default=_MISSING):
        value = self._raw(name, default)
        return default if value is _MISSING else value

    def bool(self, name: str, default=_MISSING):
        value = self._raw(name, default)
        if value is _MISSING:
            return default
        lowered = value.lower()
        if lowered in _TRUE:
            return True
        if lowered in _FALSE:
            return False
        raise ImproperlyConfigured(f"The {name} environment variable must be a boolean.")

    def int(self, name: str, default=_MISSING):
        value = self._raw(name, default)
        if value is _MISSING:
            return default
        try:
            return int(value)
        except ValueError:
            raise ImproperlyConfigured(
                f"The {name} environment variable must be an integer."
            ) from None

    def list(self, name: str, default=_MISSING):
        """A comma-separated list; blank entries are dropped."""
        value = self._raw(name, default)
        if value is _MISSING:
            return list(default)
        items = [item.strip() for item in value.split(",") if item.strip()]
        if not items and default is _MISSING:
            raise ImproperlyConfigured(f"The {name} environment variable is required.")
        return items

    def database_url(self, name: str, default=_MISSING):
        """A `postgres://user:password@host:port/name?option=value` URL as a DATABASES entry."""
        value = self._raw(name, default)
        if value is _MISSING:
            return default
        return parse_database_url(value, name)


def parse_database_url(url: str, name: str = "DATABASE_URL") -> dict:
    parts = urlsplit(url)
    if parts.scheme not in {"postgres", "postgresql"}:
        raise ImproperlyConfigured(f"The {name} environment variable must be a postgres:// URL.")
    database = unquote(parts.path.lstrip("/"))
    if not database or not parts.hostname:
        raise ImproperlyConfigured(
            f"The {name} environment variable must name a host and a database."
        )
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": database,
        "USER": unquote(parts.username or ""),
        "PASSWORD": unquote(parts.password or ""),
        "HOST": parts.hostname,
        "PORT": str(parts.port or ""),
        "OPTIONS": dict(parse_qsl(parts.query)),
        "CONN_MAX_AGE": 60,
    }


def validate_origins(origins: list[str], *, name: str) -> list[str]:
    """Check each origin is an explicit scheme://host[:port], never a wildcard.

    ADS-SEC-005-01 and ADS-SEC-005-03 build the CORS allowlist and the CSRF trusted
    origins from explicit origins; a wildcard fails settings load.
    """
    validated = []
    for origin in origins:
        if "*" in origin:
            raise ImproperlyConfigured(
                f"The {name} environment variable must not contain a wildcard origin."
            )
        parts = urlsplit(origin)
        if (
            parts.scheme not in {"http", "https"}
            or not parts.hostname
            or parts.path not in {"", "/"}
            or parts.query
            or parts.fragment
        ):
            raise ImproperlyConfigured(
                f"The {name} environment variable contains {origin!r}, which is not an explicit "
                "scheme://host[:port] origin."
            )
        validated.append(f"{parts.scheme}://{parts.netloc}")
    return validated


def load_env_file(path) -> None:
    """Load KEY=VALUE lines from a local `.env` file without overriding the real environment.

    Used only by `manage.py` for local development convenience; production reads the
    platform's environment and the test suite reads neither.
    """
    try:
        with open(path, encoding="utf-8") as handle:
            lines = handle.readlines()
    except FileNotFoundError:
        return
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key.startswith("export "):
            key = key[len("export ") :].strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)
