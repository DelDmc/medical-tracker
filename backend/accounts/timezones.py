"""The backend-supported timezone set (ADS-FR-004-01).

Identifiers come from Python's IANA timezone database (`zoneinfo`, backed by the
pinned `tzdata` package so every host agrees). An identifier is accepted only when it
matches a supported value exactly, and it is stored as that value.
"""

import zoneinfo
from functools import lru_cache


@lru_cache(maxsize=1)
def supported_timezones() -> frozenset[str]:
    return frozenset(zoneinfo.available_timezones())


def canonical_timezone(value: object) -> str:
    """Return the supported identifier equal to `value`, or raise `ValueError`."""
    if isinstance(value, str) and value in supported_timezones():
        return value
    raise ValueError(f"{value!r} is not a supported timezone.")
