"""Tests for cronparse.timezone module."""

import pytest
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # type: ignore

from cronparse.timezone import (
    TimezoneError,
    get_timezone,
    localize,
    to_utc,
    list_common_timezones,
)


def test_get_timezone_valid():
    tz = get_timezone("America/New_York")
    assert tz.key == "America/New_York"


def test_get_timezone_utc():
    tz = get_timezone("UTC")
    assert tz.key == "UTC"


def test_get_timezone_invalid_raises():
    with pytest.raises(TimezoneError, match="Unknown timezone"):
        get_timezone("Mars/Olympus_Mons")


def test_localize_naive_datetime():
    naive = datetime(2024, 6, 1, 12, 0, 0)
    aware = localize(naive, "Europe/London")
    assert aware.tzinfo is not None
    assert aware.hour == 12


def test_localize_aware_datetime_converts():
    utc_dt = datetime(2024, 6, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
    ny_dt = localize(utc_dt, "America/New_York")
    # UTC-4 in summer (EDT)
    assert ny_dt.hour == 8


def test_localize_invalid_tz_raises():
    naive = datetime(2024, 1, 1, 0, 0)
    with pytest.raises(TimezoneError):
        localize(naive, "Fake/Zone")


def test_to_utc_from_aware():
    ny_tz = ZoneInfo("America/New_York")
    ny_dt = datetime(2024, 6, 1, 8, 0, 0, tzinfo=ny_tz)
    utc_dt = to_utc(ny_dt)
    assert utc_dt.tzinfo == ZoneInfo("UTC")
    assert utc_dt.hour == 12


def test_to_utc_naive_raises():
    naive = datetime(2024, 1, 1, 0, 0)
    with pytest.raises(ValueError, match="naive"):
        to_utc(naive)


def test_list_common_timezones_contains_utc():
    tzs = list_common_timezones()
    assert "UTC" in tzs


def test_list_common_timezones_returns_list():
    tzs = list_common_timezones()
    assert isinstance(tzs, list)
    assert len(tzs) > 0


def test_list_common_timezones_all_valid():
    for tz_name in list_common_timezones():
        tz = get_timezone(tz_name)
        assert tz is not None
