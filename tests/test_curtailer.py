"""Tests for cronparse.curtailer."""

from datetime import datetime, timezone

import pytest

from cronparse.curtailer import CurtailResult, curtail, curtail_many


def dt(hour: int = 0, minute: int = 0) -> datetime:
    return datetime(2024, 1, 15, hour, minute, 0, tzinfo=timezone.utc)


# --- basic return type ---

def test_curtail_returns_curtail_result():
    result = curtail("* * * * *", dt())
    assert isinstance(result, CurtailResult)


def test_curtail_stores_expression():
    result = curtail("0 * * * *", dt())
    assert result.expression == "0 * * * *"


def test_curtail_label_none_by_default():
    result = curtail("* * * * *", dt())
    assert result.label is None


def test_curtail_label_propagated():
    result = curtail("* * * * *", dt(), label="my-job")
    assert result.label == "my-job"


def test_curtail_stores_limit():
    result = curtail("* * * * *", dt(), limit=5)
    assert result.limit == 5


def test_curtail_stores_window_hours():
    result = curtail("* * * * *", dt(), window_hours=6)
    assert result.window_hours == 6


# --- count / cap behaviour ---

def test_curtail_every_minute_respects_limit():
    result = curtail("* * * * *", dt(), limit=5, window_hours=24)
    assert result.count == 5


def test_curtail_every_minute_is_capped():
    result = curtail("* * * * *", dt(), limit=5, window_hours=24)
    assert result.capped is True


def test_curtail_hourly_within_small_window_not_capped():
    # 0 * * * * fires once per hour; 2-hour window => 2 runs, limit=10
    result = curtail("0 * * * *", dt(), limit=10, window_hours=2)
    assert result.count == 2
    assert result.capped is False


def test_curtail_specific_time_outside_window_returns_empty():
    # fires at 23:30; window is 1 hour from 00:00 => no runs
    result = curtail("30 23 * * *", dt(0, 0), limit=10, window_hours=1)
    assert result.count == 0
    assert result.capped is False


def test_curtail_first_and_last_none_when_empty():
    result = curtail("30 23 * * *", dt(0, 0), limit=10, window_hours=1)
    assert result.first is None
    assert result.last is None


def test_curtail_first_is_earliest_run():
    result = curtail("* * * * *", dt(0, 0), limit=3, window_hours=1)
    assert result.first == result.runs[0]


def test_curtail_last_is_latest_run():
    result = curtail("* * * * *", dt(0, 0), limit=3, window_hours=1)
    assert result.last == result.runs[-1]


# --- validation ---

def test_curtail_invalid_limit_raises():
    with pytest.raises(ValueError, match="limit"):
        curtail("* * * * *", dt(), limit=0)


def test_curtail_invalid_window_raises():
    with pytest.raises(ValueError, match="window_hours"):
        curtail("* * * * *", dt(), window_hours=0)


# --- str ---

def test_curtail_str_contains_expression_info():
    result = curtail("* * * * *", dt(), limit=5)
    s = str(result)
    assert "5" in s
    assert "capped" in s


# --- curtail_many ---

def test_curtail_many_returns_list():
    results = curtail_many(["* * * * *", "0 * * * *"], dt())
    assert isinstance(results, list)
    assert len(results) == 2


def test_curtail_many_assigns_labels():
    results = curtail_many(["* * * * *", "0 * * * *"], dt(), labels=["a", "b"])
    assert results[0].label == "a"
    assert results[1].label == "b"


def test_curtail_many_label_mismatch_raises():
    with pytest.raises(ValueError):
        curtail_many(["* * * * *", "0 * * * *"], dt(), labels=["only-one"])
