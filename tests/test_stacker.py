"""Tests for cronparse.stacker."""
from datetime import datetime, timedelta

import pytest

from cronparse.stacker import StackEntry, StackResult, stack


@pytest.fixture()
def anchor() -> datetime:
    return datetime(2024, 1, 15, 12, 0, 0)


# ---------------------------------------------------------------------------
# Return type
# ---------------------------------------------------------------------------

def test_stack_returns_stack_result(anchor):
    result = stack(["* * * * *"], n=3, start=anchor)
    assert isinstance(result, StackResult)


def test_stack_entries_are_stack_entry_instances(anchor):
    result = stack(["* * * * *"], n=3, start=anchor)
    for entry in result.entries:
        assert isinstance(entry, StackEntry)


# ---------------------------------------------------------------------------
# Count / ordering
# ---------------------------------------------------------------------------

def test_stack_single_expression_count_equals_n(anchor):
    result = stack(["* * * * *"], n=5, start=anchor)
    assert result.count == 5


def test_stack_two_expressions_count_equals_two_n(anchor):
    result = stack(["* * * * *", "0 * * * *"], n=4, start=anchor)
    assert result.count == 8


def test_stack_entries_are_sorted_ascending(anchor):
    result = stack(["0 * * * *", "30 * * * *"], n=3, start=anchor)
    times = [e.run_at for e in result.entries]
    assert times == sorted(times)


# ---------------------------------------------------------------------------
# first / last helpers
# ---------------------------------------------------------------------------

def test_stack_first_is_earliest(anchor):
    result = stack(["* * * * *"], n=5, start=anchor)
    assert result.first.run_at == min(e.run_at for e in result.entries)


def test_stack_last_is_latest(anchor):
    result = stack(["* * * * *"], n=5, start=anchor)
    assert result.last.run_at == max(e.run_at for e in result.entries)


def test_stack_empty_expressions_returns_empty_result(anchor):
    result = stack([], n=5, start=anchor)
    assert result.count == 0
    assert result.first is None
    assert result.last is None


# ---------------------------------------------------------------------------
# Labels
# ---------------------------------------------------------------------------

def test_stack_labels_propagated(anchor):
    result = stack(["* * * * *"], n=2, start=anchor, labels=["my-job"])
    for entry in result.entries:
        assert entry.label == "my-job"


def test_stack_no_label_is_none(anchor):
    result = stack(["* * * * *"], n=2, start=anchor)
    for entry in result.entries:
        assert entry.label is None


def test_stack_label_length_mismatch_raises(anchor):
    with pytest.raises(ValueError):
        stack(["* * * * *", "0 * * * *"], n=2, start=anchor, labels=["only-one"])


def test_stack_by_label_filters_correctly(anchor):
    result = stack(
        ["* * * * *", "0 * * * *"],
        n=3,
        start=anchor,
        labels=["minutely", "hourly"],
    )
    minutely = result.by_label("minutely")
    assert len(minutely) == 3
    assert all(e.label == "minutely" for e in minutely)


# ---------------------------------------------------------------------------
# expressions / labels stored
# ---------------------------------------------------------------------------

def test_stack_stores_expressions(anchor):
    exprs = ["* * * * *", "0 * * * *"]
    result = stack(exprs, n=1, start=anchor)
    assert result.expressions == exprs


def test_stack_stores_labels(anchor):
    result = stack(["* * * * *"], n=1, start=anchor, labels=["j1"])
    assert result.labels == ["j1"]


# ---------------------------------------------------------------------------
# summary / str
# ---------------------------------------------------------------------------

def test_stack_summary_contains_count(anchor):
    result = stack(["* * * * *"], n=5, start=anchor)
    assert "5" in result.summary()


def test_stack_entry_str_contains_expression(anchor):
    result = stack(["* * * * *"], n=1, start=anchor)
    assert "* * * * *" in str(result.entries[0])


def test_stack_entry_str_contains_label_when_set(anchor):
    result = stack(["* * * * *"], n=1, start=anchor, labels=["heartbeat"])
    assert "heartbeat" in str(result.entries[0])
