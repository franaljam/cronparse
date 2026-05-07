"""Tests for cronparse.windower."""

import pytest
from datetime import datetime, timezone

from cronparse.windower import WindowResult, window, window_many


@pytest.fixture()
def start():
    return datetime(2024, 1, 15, 9, 0, 0, tzinfo=timezone.utc)


def test_window_returns_window_result(start):
    result = window("* * * * *", start, hours=1)
    assert isinstance(result, WindowResult)


def test_window_stores_expression(start):
    result = window("0 * * * *", start, hours=1)
    assert result.expression == "0 * * * *"


def test_window_stores_start_and_end(start):
    from datetime import timedelta
    result = window("* * * * *", start, hours=2)
    assert result.start == start
    assert result.end == start + timedelta(hours=2)


def test_window_every_minute_count_equals_hours_times_60(start):
    result = window("* * * * *", start, hours=1)
    assert result.count == 60


def test_window_hourly_count_equals_hours(start):
    result = window("0 * * * *", start, hours=3)
    assert result.count == 3


def test_window_specific_time_outside_window_returns_zero(start):
    # 23:00 is outside the 1-hour window starting at 09:00
    result = window("0 23 * * *", start, hours=1)
    assert result.count == 0


def test_window_specific_time_inside_window_returns_one(start):
    # 09:30 is inside the 1-hour window starting at 09:00
    result = window("30 9 * * *", start, hours=1)
    assert result.count == 1


def test_window_label_propagated(start):
    result = window("* * * * *", start, hours=1, label="my-job")
    assert result.label == "my-job"


def test_window_label_none_by_default(start):
    result = window("* * * * *", start, hours=1)
    assert result.label is None


def test_window_first_is_datetime_or_none(start):
    result = window("* * * * *", start, hours=1)
    assert isinstance(result.first, datetime)


def test_window_last_is_datetime_or_none(start):
    result = window("* * * * *", start, hours=1)
    assert isinstance(result.last, datetime)


def test_window_no_runs_first_last_none(start):
    result = window("0 23 * * *", start, hours=1)
    assert result.first is None
    assert result.last is None


def test_window_str_contains_expression(start):
    result = window("0 * * * *", start, hours=1)
    assert "0 * * * *" in str(result)


def test_window_str_contains_count(start):
    result = window("0 * * * *", start, hours=3)
    assert "3" in str(result)


def test_window_invalid_hours_raises(start):
    with pytest.raises(ValueError):
        window("* * * * *", start, hours=0)


def test_window_many_returns_list(start):
    results = window_many(["* * * * *", "0 * * * *"], start, hours=1)
    assert isinstance(results, list)
    assert len(results) == 2


def test_window_many_label_mismatch_raises(start):
    with pytest.raises(ValueError):
        window_many(["* * * * *"], start, labels=["a", "b"])


def test_window_many_labels_assigned(start):
    results = window_many(["* * * * *", "0 * * * *"], start, labels=["j1", "j2"])
    assert results[0].label == "j1"
    assert results[1].label == "j2"
