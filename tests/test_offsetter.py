"""Tests for cronparse.offsetter."""
from datetime import datetime, timedelta

import pytest

from cronparse.offsetter import OffsetResult, offset, offset_many


@pytest.fixture
def dt():
    return datetime(2024, 1, 15, 12, 0, 0)


def test_offset_returns_offset_result(dt):
    result = offset("* * * * *", 5, start=dt, n=3)
    assert isinstance(result, OffsetResult)


def test_offset_stores_expression(dt):
    result = offset("0 9 * * *", 10, start=dt, n=2)
    assert result.expression == "0 9 * * *"


def test_offset_stores_offset_minutes(dt):
    result = offset("* * * * *", 15, start=dt, n=2)
    assert result.offset_minutes == 15


def test_offset_label_none_by_default(dt):
    result = offset("* * * * *", 5, start=dt)
    assert result.label is None


def test_offset_label_propagated(dt):
    result = offset("* * * * *", 5, start=dt, label="my-job")
    assert result.label == "my-job"


def test_offset_count_matches_n(dt):
    result = offset("* * * * *", 5, start=dt, n=7)
    assert result.count == 7


def test_offset_original_runs_length(dt):
    result = offset("* * * * *", 5, start=dt, n=4)
    assert len(result.original_runs) == 4


def test_offset_runs_shifted_by_offset(dt):
    result = offset("* * * * *", 10, start=dt, n=3)
    for orig, shifted in zip(result.original_runs, result.offset_runs):
        assert shifted == orig + timedelta(minutes=10)


def test_offset_negative_offset(dt):
    result = offset("* * * * *", -5, start=dt, n=3)
    for orig, shifted in zip(result.original_runs, result.offset_runs):
        assert shifted == orig - timedelta(minutes=5)


def test_offset_zero_offset_runs_equal(dt):
    result = offset("* * * * *", 0, start=dt, n=3)
    assert result.original_runs == result.offset_runs


def test_offset_first_property(dt):
    result = offset("* * * * *", 5, start=dt, n=3)
    assert result.first == result.offset_runs[0]


def test_offset_last_property(dt):
    result = offset("* * * * *", 5, start=dt, n=3)
    assert result.last == result.offset_runs[-1]


def test_offset_str_contains_expression(dt):
    result = offset("0 6 * * *", 30, start=dt, n=2)
    assert "0 6 * * *" in str(result)


def test_offset_str_contains_offset(dt):
    result = offset("* * * * *", 15, start=dt, n=2)
    assert "+15" in str(result)


def test_offset_many_returns_list(dt):
    results = offset_many(["* * * * *", "0 * * * *"], 5, start=dt, n=2)
    assert isinstance(results, list)
    assert len(results) == 2


def test_offset_many_all_are_offset_results(dt):
    results = offset_many(["* * * * *", "0 * * * *"], 5, start=dt, n=2)
    for r in results:
        assert isinstance(r, OffsetResult)


def test_offset_many_labels_propagated(dt):
    results = offset_many(
        ["* * * * *", "0 * * * *"], 5, start=dt, n=2, labels=["a", "b"]
    )
    assert results[0].label == "a"
    assert results[1].label == "b"


def test_offset_many_label_length_mismatch_raises(dt):
    with pytest.raises(ValueError):
        offset_many(["* * * * *", "0 * * * *"], 5, start=dt, labels=["only-one"])
