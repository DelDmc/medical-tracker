"""Explicit CSRF enforcement for the cookie-authenticated auth endpoints (ADS-SEC-005-05).

DRF views are CSRF-exempt, and DRF only re-applies CSRF under session authentication,
which this API does not use. `login`, `refresh` and `logout` therefore call
`enforce_csrf` themselves: the request needs the CSRF cookie and a matching
`X-CSRFToken` header, and a cross-origin request needs a trusted `Origin`.
"""

from django.middleware.csrf import CsrfViewMiddleware
from rest_framework.exceptions import PermissionDenied

CSRF_FAILURE = "CSRF verification failed."


class _CSRFCheck(CsrfViewMiddleware):
    def _reject(self, request, reason):
        return reason


def enforce_csrf(request) -> None:
    """Raise `403 {"detail": "CSRF verification failed."}` unless the request passes."""
    django_request = getattr(request, "_request", request)
    check = _CSRFCheck(lambda _request: None)
    check.process_request(django_request)
    if check.process_view(django_request, None, (), {}):
        raise PermissionDenied(CSRF_FAILURE)
