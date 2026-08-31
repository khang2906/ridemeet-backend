"""Timezone helpers.

The rule for the whole app: **UTC everywhere inside, local time only at the
edges.** Anything arriving from a form or an API body gets converted on the way
in; rendering back into someone's local time is the frontend's job.

Naive datetimes are treated as Munich local time, because that's what they are:
an HTML `datetime-local` input and the Jinja form both submit the wall clock the
user was looking at, with no offset attached.
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# RideMeet is a Munich app; this is the zone its users type times in.
# ZoneInfo (not a fixed +01:00/+02:00 offset) so DST is handled correctly —
# the same wall-clock time maps to a different UTC time in summer and winter.
LOCAL_TZ = ZoneInfo("Europe/Berlin")


def to_utc(value: datetime) -> datetime:
    """Convert a datetime to UTC, treating naive input as Munich local time."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=LOCAL_TZ)
    return value.astimezone(timezone.utc)


def utc_now() -> datetime:
    """Timezone-aware 'now' in UTC — never use datetime.now() for comparisons."""
    return datetime.now(timezone.utc)
