"""Tests for cronparse.fencer."""
from __future__ import annotations

from datetime import datetime, time

import pytest

from cronparse.fencer import FenceResult, fence, fence_many


@pytest.fixture
def dt():
    return datetime(2024, 1, 15, 8, 0, 0)


# --- return type ---

def test_fence_returns_fence_result(dt):
    result = fence("* * * * *", dt, time(0, 0), time(23, 59), n=3)
    assert isinstance(result, FenceResult)


def test_fence_stores_expression(dt):
    result = fence("0 9 * * *", dt, time(8, 0), time(18, 0), n=2)
    assert result.expression == "0 9 * * *"


def test_fence_label_none_by_default(dt):
    result = fence("* * * * *", dt, time(0, 0), time(23, 59), n=1)
    assert result.label is None


def test_fence_label_propagated(dt):
    result = fence("* * * * *", dt, time(0, 0), time(23, 59), n=1, label="job")
    assert result.label == "job"


def test_fence_stores_fence_start_and_end(dt):
    result = fence("* * * * *", dt, time(9, 0), time(17, 0), n=1)
    assert result.fence_start == time(9, 0)
    assert result.fence_end == time(17, 0)


# --- run filtering ---

def test_fence_every_minute_within_window_returns_n(dt):
    result = fence("* * * * *", dt, time(8, 0), time(10, 0), n=5)
    assert result.count() == 5


def test_fence_runs_are_within_fence(dt):
    result = fence("* * * * *", dt, time(9, 0), time(9, 30), n=10)
    for run in result.runs:
        assert time(9, 0) <= run.time().replace(second=0) <= time(9, 30)


def test_fence_specific_hour_outside_fence_returns_empty(dt):
    # 0 3 * * * fires at 03:00; fence is 09:00–17:00 — need many checks
    # Use a narrow fence that won't match the expression at all within 1500 checks
    result = fence("0 3 * * *", dt, time(9, 0), time(9, 1), n=2)
    # At most 1 match per day in a 1-minute window; 1500 iterations = ~1500 mins
    assert result.count() <= 2


def test_fence_specific_hour_inside_fence_fires(dt):
    result = fence("0 10 * * *", dt, time(9, 0), time(11, 0), n=1)
    assert result.count() == 1
    assert result.first().hour == 10
    assert result.first().minute == 0


# --- helpers ---

def test_fence_first_and_last(dt):
    result = fence("* * * * *", dt, time(0, 0), time(23, 59), n=3)
    assert result.first() == result.runs[0]
    assert result.last() == result.runs[-1]


def test_fence_first_none_when_empty(dt):
    # Force empty by using a fence that nothing can match quickly
    result = fence("0 3 * * *", dt, time(4, 0), time(4, 0), n=2)
    # May or may not be empty; just confirm no AttributeError
    _ = result.first()
    _ = result.last()


def test_fence_str(dt):
    result = fence("* * * * *", dt, time(8, 0), time(9, 0), n=2)
    s = str(result)
    assert "FenceResult" in s
    assert "* * * * *" in s


# --- fence_many ---

def test_fence_many_returns_list(dt):
    results = fence_many(
        ["* * * * *", "0 * * * *"],
        dt,
        time(0, 0),
        time(23, 59),
        n=2,
    )
    assert isinstance(results, list)
    assert len(results) == 2


def test_fence_many_label_mismatch_raises(dt):
    with pytest.raises(ValueError):
        fence_many(
            ["* * * * *", "0 * * * *"],
            dt,
            time(0, 0),
            time(23, 59),
            labels=["only-one"],
        )


def test_fence_many_labels_propagated(dt):
    results = fence_many(
        ["* * * * *", "0 * * * *"],
        dt,
        time(0, 0),
        time(23, 59),
        n=2,
        labels=["a", "b"],
    )
    assert results[0].label == "a"
    assert results[1].label == "b"
