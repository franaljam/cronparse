"""Tests for cronparse.estimator."""

from datetime import datetime, timezone, timedelta

import pytest

from cronparse.estimator import estimate, estimate_many, EstimateResult


def dt(year=2024, month=1, day=1, hour=0, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)


START = dt()
ONE_DAY_END = dt(day=2)
ONE_HOUR_END = dt(hour=1)


def test_estimate_returns_estimate_result():
    result = estimate("* * * * *", START, ONE_HOUR_END)
    assert isinstance(result, EstimateResult)


def test_estimate_every_minute_one_hour():
    result = estimate("* * * * *", START, ONE_HOUR_END)
    assert result.estimated_count == 60


def test_estimate_every_minute_one_day():
    result = estimate("* * * * *", START, ONE_DAY_END)
    assert result.estimated_count == 1440


def test_estimate_hourly_one_day():
    result = estimate("0 * * * *", START, ONE_DAY_END)
    assert result.estimated_count == 24


def test_estimate_specific_time_one_day():
    # Fires at 09:30 every day
    result = estimate("30 9 * * *", START, ONE_DAY_END)
    assert result.estimated_count == 1


def test_estimate_specific_time_not_in_window():
    # Window is 00:00 to 01:00; 09:30 never fires
    result = estimate("30 9 * * *", START, ONE_HOUR_END)
    assert result.estimated_count == 0


def test_estimate_runs_per_day_every_minute():
    result = estimate("* * * * *", START, ONE_DAY_END)
    assert abs(result.runs_per_day - 1440.0) < 1.0


def test_estimate_stores_expression():
    result = estimate("0 * * * *", START, ONE_DAY_END)
    assert result.expression == "0 * * * *"


def test_estimate_stores_label():
    result = estimate("0 * * * *", START, ONE_DAY_END, label="hourly")
    assert result.label == "hourly"


def test_estimate_no_label_is_none():
    result = estimate("0 * * * *", START, ONE_DAY_END)
    assert result.label is None


def test_estimate_stores_window():
    result = estimate("* * * * *", START, ONE_HOUR_END)
    assert result.window_start == START
    assert result.window_end == ONE_HOUR_END


def test_estimate_invalid_window_raises():
    with pytest.raises(ValueError, match="window_end must be after"):
        estimate("* * * * *", ONE_HOUR_END, START)


def test_estimate_str_contains_expression():
    result = estimate("0 * * * *", START, ONE_DAY_END, label="hourly")
    text = str(result)
    assert "0 * * * *" in text
    assert "hourly" in text


def test_estimate_summary_contains_count():
    result = estimate("0 * * * *", START, ONE_DAY_END)
    assert "24" in result.summary()


def test_estimate_many_returns_list():
    results = estimate_many(["* * * * *", "0 * * * *"], START, ONE_DAY_END)
    assert isinstance(results, list)
    assert len(results) == 2


def test_estimate_many_with_labels():
    results = estimate_many(
        ["* * * * *", "0 * * * *"],
        START,
        ONE_DAY_END,
        labels=["frequent", "hourly"],
    )
    assert results[0].label == "frequent"
    assert results[1].label == "hourly"


def test_estimate_many_label_mismatch_raises():
    with pytest.raises(ValueError, match="labels length"):
        estimate_many(["* * * * *", "0 * * * *"], START, ONE_DAY_END, labels=["only_one"])
