"""Tests for cronparse.cycler."""
import pytest
from datetime import datetime, timezone

from cronparse.cycler import CycleResult, cycle, _compute_gaps


@pytest.fixture
def anchor():
    return datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)


# --- _compute_gaps -----------------------------------------------------------

def test_compute_gaps_empty():
    assert _compute_gaps([]) == []


def test_compute_gaps_single():
    from datetime import timedelta
    base = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
    assert _compute_gaps([base]) == []


def test_compute_gaps_two_runs():
    from datetime import timedelta
    base = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
    runs = [base, base + timedelta(minutes=5)]
    assert _compute_gaps(runs) == [5]


def test_compute_gaps_multiple():
    from datetime import timedelta
    base = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
    runs = [base + timedelta(minutes=i * 10) for i in range(4)]
    assert _compute_gaps(runs) == [10, 10, 10]


# --- cycle() return type -----------------------------------------------------

def test_cycle_returns_cycle_result(anchor):
    result = cycle("* * * * *", anchor=anchor, sample_size=5)
    assert isinstance(result, CycleResult)


def test_cycle_stores_expression(anchor):
    result = cycle("0 * * * *", anchor=anchor)
    assert result.expression == "0 * * * *"


def test_cycle_label_none_by_default(anchor):
    result = cycle("* * * * *", anchor=anchor)
    assert result.label is None


def test_cycle_label_propagated(anchor):
    result = cycle("* * * * *", anchor=anchor, label="minutely")
    assert result.label == "minutely"


def test_cycle_sample_size_stored(anchor):
    result = cycle("* * * * *", anchor=anchor, sample_size=10)
    assert result.sample_size == 10


# --- every-minute schedule ---------------------------------------------------

def test_every_minute_is_regular(anchor):
    result = cycle("* * * * *", anchor=anchor, sample_size=10)
    assert result.is_regular is True


def test_every_minute_interval_is_one(anchor):
    result = cycle("* * * * *", anchor=anchor, sample_size=10)
    assert result.interval_minutes == 1


def test_every_minute_jitter_is_zero(anchor):
    result = cycle("* * * * *", anchor=anchor, sample_size=10)
    assert result.jitter == pytest.approx(0.0)


def test_every_minute_gap_count_is_sample_minus_one(anchor):
    result = cycle("* * * * *", anchor=anchor, sample_size=10)
    assert result.count == 9


# --- every-5-minutes schedule ------------------------------------------------

def test_step_5_interval_is_5(anchor):
    result = cycle("*/5 * * * *", anchor=anchor, sample_size=10)
    assert result.interval_minutes == 5


def test_step_5_is_regular(anchor):
    result = cycle("*/5 * * * *", anchor=anchor, sample_size=10)
    assert result.is_regular is True


# --- hourly schedule ---------------------------------------------------------

def test_hourly_interval_is_60(anchor):
    result = cycle("0 * * * *", anchor=anchor, sample_size=6)
    assert result.interval_minutes == 60


def test_hourly_mean_gap(anchor):
    result = cycle("0 * * * *", anchor=anchor, sample_size=6)
    assert result.mean_gap == pytest.approx(60.0)


# --- summary / str -----------------------------------------------------------

def test_summary_contains_expression(anchor):
    result = cycle("* * * * *", anchor=anchor)
    assert "* * * * *" in result.summary()


def test_summary_contains_interval(anchor):
    result = cycle("* * * * *", anchor=anchor)
    assert "1" in result.summary()


def test_str_contains_expression(anchor):
    result = cycle("*/10 * * * *", anchor=anchor)
    assert "*/10 * * * *" in str(result)
