"""Tests for cronparse.batcher."""

from datetime import datetime, timedelta

import pytest

from cronparse.batcher import BatchResult, BatchWindow, batch


@pytest.fixture
def dt():
    return datetime(2024, 1, 15, 8, 0, 0)


def test_batch_returns_batch_result(dt):
    result = batch("* * * * *", dt, num_windows=3, batch_minutes=60)
    assert isinstance(result, BatchResult)


def test_batch_stores_expression(dt):
    result = batch("0 * * * *", dt, num_windows=2, batch_minutes=60)
    assert result.expression == "0 * * * *"


def test_batch_label_none_by_default(dt):
    result = batch("* * * * *", dt, num_windows=2, batch_minutes=60)
    assert result.label is None


def test_batch_label_propagated(dt):
    result = batch("* * * * *", dt, num_windows=2, batch_minutes=60, label="my-job")
    assert result.label == "my-job"


def test_batch_stores_batch_minutes(dt):
    result = batch("* * * * *", dt, num_windows=2, batch_minutes=30)
    assert result.batch_minutes == 30


def test_batch_window_count_matches_num_windows(dt):
    result = batch("* * * * *", dt, num_windows=5, batch_minutes=60)
    assert result.count == 5


def test_batch_windows_are_batch_window_instances(dt):
    result = batch("* * * * *", dt, num_windows=3, batch_minutes=60)
    for w in result.windows:
        assert isinstance(w, BatchWindow)


def test_batch_window_index_starts_at_one(dt):
    result = batch("* * * * *", dt, num_windows=3, batch_minutes=60)
    assert result.windows[0].index == 1
    assert result.windows[1].index == 2
    assert result.windows[2].index == 3


def test_batch_window_starts_are_contiguous(dt):
    result = batch("* * * * *", dt, num_windows=3, batch_minutes=60)
    for i, w in enumerate(result.windows):
        expected_start = dt + timedelta(minutes=60 * i)
        assert w.start == expected_start


def test_batch_window_end_equals_next_start(dt):
    result = batch("* * * * *", dt, num_windows=3, batch_minutes=60)
    for i in range(len(result.windows) - 1):
        assert result.windows[i].end == result.windows[i + 1].start


def test_batch_every_minute_fills_windows(dt):
    result = batch("* * * * *", dt, num_windows=2, batch_minutes=60)
    for w in result.windows:
        assert w.count == 60


def test_batch_hourly_one_run_per_window(dt):
    result = batch("0 * * * *", dt, num_windows=3, batch_minutes=60)
    for w in result.windows:
        assert w.count == 1


def test_batch_total_runs_sums_windows(dt):
    result = batch("* * * * *", dt, num_windows=2, batch_minutes=60)
    assert result.total_runs == sum(w.count for w in result.windows)


def test_batch_non_empty_windows_excludes_empty(dt):
    # Specific time that only fires once in 3 hours
    result = batch("0 9 * * *", dt, num_windows=3, batch_minutes=60)
    for w in result.non_empty_windows:
        assert not w.is_empty


def test_batch_is_empty_property(dt):
    result = batch("0 9 * * *", dt, num_windows=3, batch_minutes=60)
    empty_windows = [w for w in result.windows if w.is_empty]
    for w in empty_windows:
        assert w.is_empty is True
        assert w.count == 0


def test_batch_summary_contains_expression(dt):
    result = batch("0 * * * *", dt, num_windows=2, batch_minutes=60)
    assert "0 * * * *" in result.summary()


def test_batch_summary_contains_run_count(dt):
    result = batch("0 * * * *", dt, num_windows=2, batch_minutes=60)
    assert str(result.total_runs) in result.summary()
