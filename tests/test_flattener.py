"""Tests for cronparse.flattener."""

import pytest
from cronparse.flattener import FlattenResult, flatten, flatten_many


# ---------------------------------------------------------------------------
# flatten() return type
# ---------------------------------------------------------------------------

def test_flatten_returns_flatten_result():
    result = flatten("0 9 * * *")
    assert isinstance(result, FlattenResult)


def test_flatten_stores_expression():
    result = flatten("0 9 * * *")
    assert result.expression == "0 9 * * *"


def test_flatten_label_none_by_default():
    result = flatten("* * * * *")
    assert result.label is None


def test_flatten_label_propagated():
    result = flatten("0 9 * * *", label="morning")
    assert result.label == "morning"


# ---------------------------------------------------------------------------
# Specific expressions
# ---------------------------------------------------------------------------

def test_flatten_every_minute_produces_1440_times():
    result = flatten("* * * * *")
    assert result.count == 1440


def test_flatten_every_minute_times_are_tuples():
    result = flatten("* * * * *")
    assert all(isinstance(t, tuple) and len(t) == 2 for t in result.times)


def test_flatten_specific_time_single_entry():
    result = flatten("30 14 * * *")
    assert result.count == 1
    assert result.times == [(14, 30)]


def test_flatten_hourly_produces_24_times():
    result = flatten("0 * * * *")
    assert result.count == 24


def test_flatten_hourly_each_hour_minute_zero():
    result = flatten("0 * * * *")
    assert all(minute == 0 for _, minute in result.times)
    assert sorted(h for h, _ in result.times) == list(range(24))


def test_flatten_step_minutes():
    # */15 fires at 0,15,30,45 — 4 times per hour × 24 hours = 96
    result = flatten("*/15 * * * *")
    assert result.count == 96


def test_flatten_times_are_sorted():
    result = flatten("*/30 */6 * * *")
    assert result.times == sorted(result.times)


def test_flatten_dom_month_dow_ignored():
    # DOM/month/DOW restrictions should not affect the intra-day count
    every_day = flatten("0 12 * * *")
    specific_dom = flatten("0 12 1 1 1")
    assert every_day.count == specific_dom.count


# ---------------------------------------------------------------------------
# flatten_many()
# ---------------------------------------------------------------------------

def test_flatten_many_returns_list():
    results = flatten_many(["* * * * *", "0 9 * * *"])
    assert isinstance(results, list)
    assert len(results) == 2


def test_flatten_many_assigns_labels():
    results = flatten_many(["* * * * *", "0 9 * * *"], labels=["a", "b"])
    assert results[0].label == "a"
    assert results[1].label == "b"


def test_flatten_many_label_mismatch_raises():
    with pytest.raises(ValueError, match="labels length"):
        flatten_many(["* * * * *", "0 9 * * *"], labels=["only_one"])


def test_flatten_many_empty_list():
    results = flatten_many([])
    assert results == []
