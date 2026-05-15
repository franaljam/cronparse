"""Tests for cronparse.jitter."""

from datetime import datetime, timedelta

import pytest

from cronparse.jitter import JitterResult, jitter, jitter_many


def dt(minute: int = 0, hour: int = 0) -> datetime:
    return datetime(2024, 1, 15, hour, minute)


# ---------------------------------------------------------------------------
# Basic return type
# ---------------------------------------------------------------------------

def test_jitter_returns_jitter_result():
    result = jitter("* * * * *", dt(), n=5, seed=0)
    assert isinstance(result, JitterResult)


def test_jitter_stores_expression():
    result = jitter("0 * * * *", dt(), n=3, seed=1)
    assert result.expression == "0 * * * *"


def test_jitter_label_none_by_default():
    result = jitter("* * * * *", dt(), n=3, seed=0)
    assert result.label is None


def test_jitter_label_propagated():
    result = jitter("* * * * *", dt(), n=3, seed=0, label="my-job")
    assert result.label == "my-job"


def test_jitter_offset_minutes_stored():
    result = jitter("* * * * *", dt(), n=3, max_offset_minutes=10, seed=0)
    assert result.offset_minutes == 10


# ---------------------------------------------------------------------------
# Run count
# ---------------------------------------------------------------------------

def test_jitter_count_matches_n():
    result = jitter("* * * * *", dt(), n=7, seed=42)
    assert result.count() == 7


def test_jitter_first_and_last():
    result = jitter("* * * * *", dt(), n=5, seed=0)
    assert result.first() == result.runs[0]
    assert result.last() == result.runs[-1]


def test_jitter_empty_runs_first_last_none():
    result = JitterResult(expression="* * * * *", offset_minutes=0, label=None, runs=[])
    assert result.first() is None
    assert result.last() is None


# ---------------------------------------------------------------------------
# Offset bounds
# ---------------------------------------------------------------------------

def test_jitter_zero_offset_matches_base_runs():
    from cronparse.parser import parse
    from cronparse.scheduler import next_runs as _next

    anchor = dt()
    expr_str = "0 * * * *"
    base = _next(parse(expr_str), anchor, 5)
    result = jitter(expr_str, anchor, n=5, max_offset_minutes=0, seed=99)
    assert result.runs == base


def test_jitter_offsets_within_bounds():
    max_off = 3
    anchor = dt()
    from cronparse.parser import parse
    from cronparse.scheduler import next_runs as _next

    base = _next(parse("* * * * *"), anchor, 20)
    result = jitter("* * * * *", anchor, n=20, max_offset_minutes=max_off, seed=7)
    for base_run, jittered_run in zip(base, result.runs):
        diff = abs((jittered_run - base_run).total_seconds() / 60)
        assert diff <= max_off


def test_jitter_negative_offset_raises():
    with pytest.raises(ValueError, match="max_offset_minutes"):
        jitter("* * * * *", dt(), max_offset_minutes=-1)


# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------

def test_jitter_same_seed_same_result():
    r1 = jitter("* * * * *", dt(), n=10, seed=123)
    r2 = jitter("* * * * *", dt(), n=10, seed=123)
    assert r1.runs == r2.runs


def test_jitter_different_seed_different_result():
    r1 = jitter("* * * * *", dt(), n=10, max_offset_minutes=5, seed=1)
    r2 = jitter("* * * * *", dt(), n=10, max_offset_minutes=5, seed=2)
    # With a wide enough offset window, seeds should differ
    assert r1.runs != r2.runs


# ---------------------------------------------------------------------------
# jitter_many
# ---------------------------------------------------------------------------

def test_jitter_many_returns_list():
    results = jitter_many(["* * * * *", "0 * * * *"], dt(), n=3, seed=0)
    assert isinstance(results, list)
    assert len(results) == 2


def test_jitter_many_label_mismatch_raises():
    with pytest.raises(ValueError):
        jitter_many(["* * * * *", "0 * * * *"], dt(), labels=["only-one"])


def test_jitter_many_labels_assigned():
    results = jitter_many(
        ["* * * * *", "0 * * * *"], dt(), n=3, seed=0, labels=["a", "b"]
    )
    assert results[0].label == "a"
    assert results[1].label == "b"


# ---------------------------------------------------------------------------
# __str__
# ---------------------------------------------------------------------------

def test_jitter_str_contains_expression():
    result = jitter("0 9 * * 1", dt(), n=3, seed=0)
    assert "0 9 * * 1" in str(result)


def test_jitter_str_contains_offset():
    result = jitter("* * * * *", dt(), n=3, max_offset_minutes=7, seed=0)
    assert "7" in str(result)
