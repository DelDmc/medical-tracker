"""The `refresh_token` cookie (api_contract.md §5.7, ADS-SEC-005-04).

HttpOnly, host-only (no Domain attribute), path `/api/v1/auth/`, expiring with the
token. `Secure`/`SameSite` come from the environment's settings. Clearing uses the
same name, path, scope and attributes as creation so browsers reliably remove it.
"""

from django.conf import settings

from config import clock

from .tokens import IssuedToken

REFRESH_COOKIE_NAME = "refresh_token"
REFRESH_COOKIE_PATH = "/api/v1/auth/"
_EPOCH = "Thu, 01 Jan 1970 00:00:00 GMT"


def _attributes():
    return {
        "path": REFRESH_COOKIE_PATH,
        "secure": settings.REFRESH_COOKIE_SECURE,
        "httponly": True,
        "samesite": settings.REFRESH_COOKIE_SAMESITE,
    }


def set_refresh_cookie(response, issued: IssuedToken) -> None:
    max_age = max(0, issued.payload["exp"] - int(clock.now().timestamp()))
    response.set_cookie(REFRESH_COOKIE_NAME, issued.token, max_age=max_age, **_attributes())


def clear_refresh_cookie(response) -> None:
    response.set_cookie(REFRESH_COOKIE_NAME, "", max_age=0, expires=_EPOCH, **_attributes())
