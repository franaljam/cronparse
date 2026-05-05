"""Timezone support utilities for cronparse."""

from datetime import datetime
from typing import Optional

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo  # type: ignore

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class TimezoneError(ValueError):
    """Raised when an invalid or unknown timezone is provided."""


def get_timezone(tz_name: str) -> ZoneInfo:
    """Return a ZoneInfo object for the given timezone name.

    Args:
        tz_name: IANA timezone string, e.g. 'America/New_York'.

    Returns:
        A ZoneInfo instance.

    Raises:
        TimezoneError: If the timezone name is not recognized.
    """
    try:
        return ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, KeyError) as exc:
        raise TimezoneError(f"Unknown timezone: {tz_name!r}") from exc


def localize(dt: datetime, tz_name: str) -> datetime:
    """Attach a timezone to a naive datetime or convert an aware one.

    Args:
        dt: A datetime object (naive or aware).
        tz_name: Target IANA timezone string.

    Returns:
        An aware datetime in the specified timezone.
    """
    tz = get_timezone(tz_name)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=tz)
    return dt.astimezone(tz)


def to_utc(dt: datetime) -> datetime:
    """Convert an aware datetime to UTC.

    Args:
        dt: An aware datetime.

    Returns:
        The equivalent datetime in UTC.

    Raises:
        ValueError: If dt is naive.
    """
    if dt.tzinfo is None:
        raise ValueError("Cannot convert naive datetime to UTC.")
    return dt.astimezone(ZoneInfo("UTC"))


def list_common_timezones() -> list:
    """Return a curated list of commonly used IANA timezone strings."""
    return [
        "UTC",
        "America/New_York",
        "America/Chicago",
        "America/Denver",
        "America/Los_Angeles",
        "Europe/London",
        "Europe/Paris",
        "Europe/Berlin",
        "Asia/Tokyo",
        "Asia/Shanghai",
        "Asia/Kolkata",
        "Australia/Sydney",
    ]
