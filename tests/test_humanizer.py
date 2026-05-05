"""Tests for the cronparse humanizer module."""

import pytest
from cronparse.parser import parse
from cronparse.humanizer import humanize


def test_every_minute():
    expr = parse("* * * * *")
    assert humanize(expr) == "every minute"


def test_specific_minute_and_hour():
    expr = parse("30 9 * * *")
    result = humanize(expr)
    assert "minute 30" in result
    assert "hour 9" in result


def test_every_minute_specific_hour():
    expr = parse("* 6 * * *")
    result = humanize(expr)
    assert "every minute" in result
    assert "hour 6" in result


def test_step_minutes():
    expr = parse("*/15 * * * *")
    result = humanize(expr)
    assert "every 15 minutes" in result


def test_range_hours():
    expr = parse("0 9-17 * * *")
    result = humanize(expr)
    assert "hour 9 through 17" in result


def test_specific_day_of_month():
    expr = parse("0 0 1 * *")
    result = humanize(expr)
    assert "day 1" in result


def test_specific_month():
    expr = parse("0 0 * 6 *")
    result = humanize(expr)
    assert "June" in result


def test_specific_weekday():
    expr = parse("0 9 * * 1")
    result = humanize(expr)
    assert "Monday" in result


def test_multiple_weekdays():
    expr = parse("0 9 * * 1,3,5")
    result = humanize(expr)
    assert "Monday" in result
    assert "Wednesday" in result
    assert "Friday" in result


def test_full_expression():
    expr = parse("30 8 1 12 1")
    result = humanize(expr)
    assert "30" in result
    assert "8" in result
    assert "December" in result
    assert "Monday" in result


def test_every_month_not_shown():
    expr = parse("0 0 * * *")
    result = humanize(expr)
    assert "every month" not in result
    assert "every day of the week" not in result
