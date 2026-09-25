"""The backend's single source of the current time (D6).

Nothing else in the backend reads the current time. Tests freeze or move it with
`freezegun`, which every call below observes.
"""

from datetime import datetime

from django.utils import timezone


def now() -> datetime:
    """The current instant as an aware UTC datetime."""
    return timezone.now()
