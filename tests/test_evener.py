"""Tests for cronparse.evener."""

from datetime import datetime

import pytest

from cronparse.evener import EvenResult, even


def dt(hour: int = 0, minute: int = 0) -> datetime:
    return datetime(2024, 1, 1, hour, minute, 0)


# ---------------------------------------------------------------------------
# Return type
# ---------------------------------------------------------------------------

def test_even_returns_even_result():
    result = even("*/15 * * * *", anchor=dt())
    assert isinstance(result, EvenResult)


def test_even_stores_expression():
    result = even("*/30 * * * *", anchor=dt())
    assert result.expression == "*/30 * * * *"


def test_even_label_none_by_default():
    result = even("* * * * *", anchor=dt())
    assert result.label is None


def test_even_label_propagated():
    result = even("* * * * *", anchor=dt(), label="all")
    assert result.label == "all"


def test_even_period_hours_stored():
    result = even("*/10 * * * *", anchor=dt(), period_hours=6)
    assert result.period_hours == 6


# ---------------------------------------------------------------------------
# Every-minute expression
# ---------------------------------------------------------------------------

def test_every_minute_run_count_equals_period_minutes():
    result = even("* * * * *", anchor=dt(), period_hours=1)
    assert result.run_count == 60


def test_every_minute_is_even():
    result = even("* * * * *", anchor=dt(), period_hours=1)
    assert result.is_even is True


def test_every_minute_variance_is_zero():
    result = even("* * * * *", anchor=dt(), period_hours=1)
    assert result.variance == pytest.approx(0.0)


def test_every_minute_min_gap_is_one():
    result = even("* * * * *", anchor=dt(), period_hours=1)
    assert result.min_gap_minutes == pytest.approx(1.0)


def test_every_minute_max_gap_is_one():
    result = even("* * * * *", anchor=dt(), period_hours=1)
    assert result.max_gap_minutes == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Step expression
# ---------------------------------------------------------------------------

def test_step_15_run_count_in_one_hour():
    result = even("*/15 * * * *", anchor=dt(), period_hours=1)
    # fires at :00, :15, :30, :45 => 4 runs
    assert result.run_count == 4


def test_step_15_is_even():
    result = even("*/15 * * * *", anchor=dt(), period_hours=1)
    assert result.is_even is True


def test_step_15_expected_gap():
    result = even("*/15 * * * *", anchor=dt(), period_hours=1)
    assert result.expected_gap_minutes == pytest.approx(20.0)


# ---------------------------------------------------------------------------
# Specific (single-fire) expression
# ---------------------------------------------------------------------------

def test_single_fire_run_count_is_one():
    result = even("0 9 * * *", anchor=dt(), period_hours=24)
    assert result.run_count == 1


def test_single_fire_gaps_are_empty():
    result = even("0 9 * * *", anchor=dt(), period_hours=24)
    assert result.actual_gaps_minutes == []


# ---------------------------------------------------------------------------
# str / summary
# ---------------------------------------------------------------------------

def test_str_contains_expression():
    result = even("*/10 * * * *", anchor=dt())
    assert "*/10 * * * *" in str(result)


def test_summary_contains_run_count():
    result = even("*/10 * * * *", anchor=dt(), period_hours=1)
    assert str(result.run_count) in result.summary()


def test_summary_contains_status_even():
    result = even("* * * * *", anchor=dt(), period_hours=1)
    assert "evenly" in result.summary()


def test_summary_contains_status_uneven():
    # two specific minutes close together -> uneven
    result = even("1,2 * * * *", anchor=dt(), period_hours=1, threshold=0.0)
    assert "unevenly" in result.summary()
