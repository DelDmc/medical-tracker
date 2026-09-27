"""The `Partitioned` attribute for the cross-site authentication cookies (ADS-SEC-005-09).

In production the frontend and the backend are different sites, so the browser treats
the CSRF and `refresh_token` cookies as third-party cookies. Browsers that block
third-party cookies still store and send a `Partitioned` one, keyed to the frontend's
site. Django 5.2 and Python 3.12 cannot emit the attribute, so this middleware appends
it to the `Set-Cookie` line of each cookie the settings mark as partitioned, including
the clearing ones, which must name the same partition.
"""

from http.cookies import Morsel

from django.conf import settings

from .cookies import REFRESH_COOKIE_NAME


class _PartitionedMorsel(Morsel):
    def OutputString(self, attrs=None):
        return f"{super().OutputString(attrs)}; Partitioned"


def _partitioned_cookie_names():
    names = []
    if settings.CSRF_COOKIE_PARTITIONED:
        names.append(settings.CSRF_COOKIE_NAME)
    if settings.REFRESH_COOKIE_PARTITIONED:
        names.append(REFRESH_COOKIE_NAME)
    return names


class PartitionedCookieMiddleware:
    """Must sit above `CsrfViewMiddleware`, which sets the CSRF cookie on the way out."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        for name in _partitioned_cookie_names():
            morsel = response.cookies.get(name)
            if morsel is None or isinstance(morsel, _PartitionedMorsel):
                continue
            partitioned = _PartitionedMorsel()
            partitioned.set(morsel.key, morsel.value, morsel.coded_value)
            partitioned.update(morsel)
            # SimpleCookie.__setitem__ would wrap the morsel in a plain one again.
            dict.__setitem__(response.cookies, name, partitioned)
        return response
