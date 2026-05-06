"""Tests for cronparse.reducer."""

import pytest
from cronparse.reducer import reduce, ReduceResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

EVERY_MINUTE = "* * * * *"
EVERY_MINUTE_ALT = "*/1 * * * *"  # semantically identical
EVERY_HOUR = "0 * * * *"
DAILY_NOON = "0 12 * * *"
DAILY_MIDNIGHT = "0 0 * * *"


# ---------------------------------------------------------------------------
# ReduceResult type
# ---------------------------------------------------------------------------

def test_reduce_returns_reduce_result():
    result = reduce([EVERY_MINUTE])
    assert isinstance(result, ReduceResult)


def test_reduce_single_expression_no_removal():
    result = reduce([EVERY_MINUTE])
    assert result.original_count == 1
    assert result.reduced == [EVERY_MINUTE]
    assert result.removed == []


def test_reduce_identical_strings_deduped():
    result = reduce([EVERY_MINUTE, EVERY_MINUTE])
    assert len(result.reduced) == 1
    assert len(result.removed) == 1


def test_reduce_semantic_duplicates_deduped():
    """*/1 * * * * is semantically the same as * * * * *."""
    result = reduce([EVERY_MINUTE, EVERY_MINUTE_ALT])
    assert len(result.reduced) == 1
    assert EVERY_MINUTE_ALT in result.removed


def test_reduce_distinct_expressions_all_kept():
    exprs = [EVERY_MINUTE, EVERY_HOUR, DAILY_NOON, DAILY_MIDNIGHT]
    result = reduce(exprs)
    assert result.reduced == exprs
    assert result.removed == []


def test_reduce_original_count_correct():
    exprs = [EVERY_MINUTE, EVERY_MINUTE, EVERY_HOUR]
    result = reduce(exprs)
    assert result.original_count == 3


def test_reduce_reduction_count_property():
    exprs = [EVERY_MINUTE, EVERY_MINUTE, EVERY_HOUR]
    result = reduce(exprs)
    assert result.reduction_count == 1


def test_reduce_empty_list():
    result = reduce([])
    assert result.original_count == 0
    assert result.reduced == []
    assert result.removed == []


# ---------------------------------------------------------------------------
# Labels
# ---------------------------------------------------------------------------

def test_reduce_labels_propagated():
    exprs = [EVERY_MINUTE, EVERY_HOUR]
    labels = ["job-a", "job-b"]
    result = reduce(exprs, labels=labels)
    assert result.labels == ["job-a", "job-b"]


def test_reduce_labels_none_by_default():
    result = reduce([EVERY_MINUTE])
    assert result.labels == [None]


def test_reduce_label_of_duplicate_dropped():
    exprs = [EVERY_MINUTE, EVERY_MINUTE]
    labels = ["first", "second"]
    result = reduce(exprs, labels=labels)
    assert result.labels == ["first"]


def test_reduce_label_length_mismatch_raises():
    with pytest.raises(ValueError, match="labels length"):
        reduce([EVERY_MINUTE, EVERY_HOUR], labels=["only-one"])


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def test_reduce_summary_returns_string():
    result = reduce([EVERY_MINUTE, EVERY_HOUR])
    s = result.summary()
    assert isinstance(s, str)


def test_reduce_summary_contains_counts():
    result = reduce([EVERY_MINUTE, EVERY_MINUTE, EVERY_HOUR])
    s = result.summary()
    assert "3" in s  # original count
    assert "2" in s  # reduced count
