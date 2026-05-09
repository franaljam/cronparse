"""Tests for cronparse.capper."""
from datetime import datetime, timezone

import pytest

from cronparse.capper import CapResult, cap, cap_many


def dt(year=2024, month=1, day=1, hour=0, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)


START = dt()
END = dt(hour=2)  # 2-hour window


def test_cap_returns_cap_result():
    result = cap("* * * * *", START, END, max_runs=5)
    assert isinstance(result, CapResult)


def test_cap_stores_expression():
    result = cap("* * * * *", START, END, max_runs=5)
    assert result.expression == "* * * * *"


def test_cap_label_none_by_default():
    result = cap("* * * * *", START, END, max_runs=5)
    assert result.label is None


def test_cap_label_propagated():
    result = cap("* * * * *", START, END, max_runs=5, label="job")
    assert result.label == "job"


def test_cap_max_runs_stored():
    result = cap("* * * * *", START, END, max_runs=10)
    assert result.cap == 10


def test_cap_every_minute_limited_to_cap():
    result = cap("* * * * *", START, END, max_runs=5)
    assert result.count == 5


def test_cap_every_minute_capped_true():
    result = cap("* * * * *", START, END, max_runs=5)
    assert result.capped is True


def test_cap_zero_max_runs_returns_empty():
    result = cap("* * * * *", START, END, max_runs=0)
    assert result.count == 0
    assert result.runs == []


def test_cap_zero_max_runs_capped_true():
    result = cap("* * * * *", START, END, max_runs=0)
    assert result.capped is True


def test_cap_negative_max_runs_raises():
    with pytest.raises(ValueError):
        cap("* * * * *", START, END, max_runs=-1)


def test_cap_hourly_within_two_hour_window_not_capped():
    # 0 0 * * * fires at 00:00 and 01:00 within [00:00, 02:00) → 2 hits, cap=10
    result = cap("0 * * * *", START, END, max_runs=10)
    assert result.count == 2
    assert result.capped is False


def test_cap_first_and_last_populated():
    result = cap("* * * * *", START, END, max_runs=3)
    assert result.first is not None
    assert result.last is not None
    assert result.first < result.last


def test_cap_first_none_when_empty():
    result = cap("0 0 * * *", START, dt(hour=0, minute=0), max_runs=5)
    assert result.first is None
    assert result.last is None


def test_cap_str_contains_expression():
    result = cap("* * * * *", START, END, max_runs=5)
    assert "* * * * *" in str(result)


def test_cap_str_contains_cap():
    result = cap("* * * * *", START, END, max_runs=5)
    assert "cap=5" in str(result)


def test_cap_many_returns_list():
    results = cap_many(["* * * * *", "0 * * * *"], START, END, max_runs=5)
    assert isinstance(results, list)
    assert len(results) == 2


def test_cap_many_all_are_cap_results():
    results = cap_many(["* * * * *", "0 * * * *"], START, END, max_runs=5)
    assert all(isinstance(r, CapResult) for r in results)


def test_cap_many_labels_propagated():
    results = cap_many(["* * * * *", "0 * * * *"], START, END, max_runs=5, labels=["a", "b"])
    assert results[0].label == "a"
    assert results[1].label == "b"


def test_cap_many_label_mismatch_raises():
    with pytest.raises(ValueError):
        cap_many(["* * * * *", "0 * * * *"], START, END, max_runs=5, labels=["only_one"])
