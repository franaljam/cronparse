"""Tests for cronparse.replayer."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from cronparse.replayer import ReplayResult, replay, replay_many


def dt(year=2024, month=6, day=15, hour=12, minute=0):
    return datetime(year, month, day, hour, minute)


START = dt(hour=9, minute=0)
END = dt(hour=10, minute=0)


def test_replay_returns_replay_result():
    result = replay("* * * * *", START, END)
    assert isinstance(result, ReplayResult)


def test_replay_stores_expression_string():
    result = replay("0 * * * *", START, END)
    assert result.expression is not None


def test_replay_every_minute_count_equals_window_minutes():
    result = replay("* * * * *", START, END)
    # 9:00 to 10:00 inclusive = 61 minutes
    assert result.count == 61


def test_replay_hourly_fires_once_in_one_hour_window():
    result = replay("0 * * * *", START, END)
    assert result.count == 2  # 9:00 and 10:00


def test_replay_specific_time_fires_when_in_window():
    result = replay("30 9 * * *", START, END)
    assert result.count == 1
    assert result.runs[0] == dt(hour=9, minute=30)


def test_replay_specific_time_does_not_fire_outside_window():
    result = replay("30 11 * * *", START, END)
    assert result.count == 0


def test_replay_label_propagated():
    result = replay("* * * * *", START, END, label="my-job")
    assert result.label == "my-job"


def test_replay_label_none_by_default():
    result = replay("* * * * *", START, END)
    assert result.label is None


def test_replay_earliest_and_latest():
    result = replay("* * * * *", START, END)
    assert result.earliest == START
    assert result.latest == END


def test_replay_empty_window_returns_no_runs():
    same = dt(hour=9, minute=0)
    result = replay("30 9 * * *", same, same)
    assert result.count == 0


def test_replay_str_contains_count():
    result = replay("0 * * * *", START, END)
    assert str(result.count) in str(result)


def test_replay_str_contains_label():
    result = replay("0 * * * *", START, END, label="job-x")
    assert "job-x" in str(result)


def test_replay_many_returns_list():
    results = replay_many(["* * * * *", "0 * * * *"], START, END)
    assert isinstance(results, list)
    assert len(results) == 2


def test_replay_many_with_labels():
    results = replay_many(["* * * * *", "0 * * * *"], START, END, labels=["a", "b"])
    assert results[0].label == "a"
    assert results[1].label == "b"


def test_replay_many_label_mismatch_raises():
    with pytest.raises(ValueError):
        replay_many(["* * * * *", "0 * * * *"], START, END, labels=["only-one"])


def test_replay_runs_are_sorted_ascending():
    result = replay("* * * * *", START, END)
    assert result.runs == sorted(result.runs)
