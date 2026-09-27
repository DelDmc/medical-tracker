"""The backend's single source of the current time (D6).

Nothing else in the backend reads the current time. Tests freeze or move it with
`freezegun`, which every call below observes. A user's "today" and "now" come only
from `user_local_now` / `user_local_date`, resolved through the account's IANA
timezone — never UTC and never the server's local time.
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from django.utils import timezone


def now() -> datetime:
    """The current instant as an aware UTC datetime."""
    return timezone.now()


def user_local_now(user) -> datetime:
    """The current instant in the user's timezone."""
    return now().astimezone(ZoneInfo(user.timezone))


def user_local_date(user) -> date:
    """The user's current local calendar date."""
    return user_local_now(user).date()
