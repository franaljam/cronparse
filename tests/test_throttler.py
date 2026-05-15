"""Tests for cronparse.throttler."""

from datetime import datetime, timedelta

import pytest

from cronparse.throttler import ThrottleResult, throttle


@pytest.fixture
def dt() -> datetime:
    return datetime(2024, 1, 15, 12, 0, 0)


def test_throttle_returns_throttle_result(dt):
    result = throttle("* * * * *", dt, total_runs=10)
    assert isinstance(result, ThrottleResult)


def test_throttle_stores_expression(dt):
    result = throttle("* * * * *", dt, total_runs=5)
    assert result.expression == "* * * * *"


def test_throttle_label_none_by_default(dt):
    result = throttle("* * * * *", dt, total_runs=5)
    assert result.label is None


def test_throttle_label_propagated(dt):
    result = throttle("* * * * *", dt, total_runs=5, label="my-job")
    assert result.label == "my-job"


def test_throttle_max_per_window_respected(dt):
    # every-minute expression, window=60 min, max 3 per window
    result = throttle("* * * * *", dt, total_runs=60, max_per_window=3, window_minutes=60)
    assert result.count <= 3


def test_throttle_no_drop_when_limit_large(dt):
    # hourly expression, 1 run per 60-min window, limit=5
    result = throttle("0 * * * *", dt, total_runs=5, max_per_window=5, window_minutes=60)
    assert result.dropped == 0
    assert result.count == 5


def test_throttle_dropped_count_is_non_negative(dt):
    result = throttle("* * * * *", dt, total_runs=30, max_per_window=2, window_minutes=10)
    assert result.dropped >= 0


def test_throttle_kept_plus_dropped_lte_total_runs(dt):
    total = 20
    result = throttle("* * * * *", dt, total_runs=total, max_per_window=3, window_minutes=60)
    assert result.count + result.dropped <= total


def test_throttle_runs_are_datetimes(dt):
    result = throttle("* * * * *", dt, total_runs=5)
    for run in result.runs:
        assert isinstance(run, datetime)


def test_throttle_runs_are_ascending(dt):
    result = throttle("* * * * *", dt, total_runs=10, max_per_window=10, window_minutes=60)
    for a, b in zip(result.runs, result.runs[1:]):
        assert a < b


def test_throttle_first_and_last(dt):
    result = throttle("0 * * * *", dt, total_runs=3, max_per_window=10, window_minutes=120)
    assert result.first == result.runs[0]
    assert result.last == result.runs[-1]


def test_throttle_first_none_when_empty(dt):
    # max_per_window=0 means nothing is ever kept
    result = throttle("* * * * *", dt, total_runs=10, max_per_window=0, window_minutes=60)
    assert result.first is None
    assert result.last is None
    assert result.count == 0


def test_throttle_str_contains_expression(dt):
    result = throttle("0 9 * * 1", dt, total_runs=5)
    assert "0 9 * * 1" in str(result)


def test_throttle_str_contains_dropped(dt):
    result = throttle("* * * * *", dt, total_runs=20, max_per_window=2, window_minutes=60)
    assert "dropped=" in str(result)


def test_throttle_max_per_window_stored(dt):
    result = throttle("* * * * *", dt, total_runs=5, max_per_window=7)
    assert result.max_per_window == 7


def test_throttle_window_minutes_stored(dt):
    result = throttle("* * * * *", dt, total_runs=5, window_minutes=30)
    assert result.window_minutes == 30
