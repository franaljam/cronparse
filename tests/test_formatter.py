"""Tests for cronparse.formatter module."""

import pytest
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # type: ignore

from cronparse.formatter import format_next_runs, format_schedule_table, format_single_run


@pytest.fixture
def utc_runs():
    tz = ZoneInfo("UTC")
    return [
        datetime(2024, 6, 1, 10, 0, tzinfo=tz),
        datetime(2024, 6, 1, 10, 1, tzinfo=tz),
        datetime(2024, 6, 1, 10, 2, tzinfo=tz),
    ]


def test_format_next_runs_returns_list(utc_runs):
    result = format_next_runs(utc_runs)
    assert isinstance(result, list)
    assert len(result) == 3


def test_format_next_runs_default_format(utc_runs):
    result = format_next_runs(utc_runs)
    assert result[0].startswith("2024-06-01 10:00:00")


def test_format_next_runs_with_timezone(utc_runs):
    result = format_next_runs(utc_runs, tz_name="America/New_York")
    # UTC 10:00 -> EDT 06:00
    assert "06:00:00" in result[0]


def test_format_next_runs_custom_fmt(utc_runs):
    result = format_next_runs(utc_runs, fmt="%H:%M")
    assert result[0] == "10:00"


def test_format_schedule_table_contains_expression(utc_runs):
    table = format_schedule_table("* * * * *", "Every minute", utc_runs)
    assert "* * * * *" in table


def test_format_schedule_table_contains_description(utc_runs):
    table = format_schedule_table("0 9 * * *", "At 09:00 every day", utc_runs)
    assert "At 09:00 every day" in table


def test_format_schedule_table_lists_runs(utc_runs):
    table = format_schedule_table("* * * * *", "Every minute", utc_runs)
    assert "1." in table
    assert "3." in table


def test_format_schedule_table_with_timezone(utc_runs):
    table = format_schedule_table("* * * * *", "Every minute", utc_runs, tz_name="UTC")
    assert "UTC" in table


def test_format_single_run_naive():
    dt = datetime(2024, 3, 15, 8, 30, 0)
    result = format_single_run(dt)
    assert result == "2024-03-15 08:30:00"


def test_format_single_run_with_tz():
    utc_dt = datetime(2024, 3, 15, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
    result = format_single_run(utc_dt, tz_name="Europe/Paris")
    assert "13:00:00" in result
