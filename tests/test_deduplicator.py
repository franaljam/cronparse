"""Tests for cronparse.deduplicator."""

import pytest

from cronparse.deduplicator import (
    DeduplicateEntry,
    DeduplicateResult,
    deduplicate,
)


# ---------------------------------------------------------------------------
# Basic return-type tests
# ---------------------------------------------------------------------------

def test_deduplicate_returns_deduplicate_result():
    result = deduplicate(["* * * * *"])
    assert isinstance(result, DeduplicateResult)


def test_deduplicate_entries_are_deduplicate_entry_instances():
    result = deduplicate(["0 * * * *", "0 12 * * *"])
    for entry in result.entries:
        assert isinstance(entry, DeduplicateEntry)


# ---------------------------------------------------------------------------
# Single expression — no duplicates
# ---------------------------------------------------------------------------

def test_single_expression_no_removal():
    result = deduplicate(["0 9 * * 1"])
    assert result.original_count == 1
    assert result.removed_count == 0
    assert result.kept_count == 1


def test_two_distinct_expressions_both_kept():
    result = deduplicate(["* * * * *", "0 12 * * *"])
    assert result.kept_count == 2
    assert result.removed_count == 0


# ---------------------------------------------------------------------------
# Exact-string duplicates
# ---------------------------------------------------------------------------

def test_identical_strings_deduplicated():
    result = deduplicate(["0 * * * *", "0 * * * *"])
    assert result.kept_count == 1
    assert result.removed_count == 1
    assert result.original_count == 2


def test_duplicate_recorded_on_first_entry():
    result = deduplicate(["0 * * * *", "0 * * * *"])
    assert result.entries[0].duplicates == ["0 * * * *"]


def test_three_identical_strings_two_removed():
    result = deduplicate(["5 4 * * *"] * 3)
    assert result.kept_count == 1
    assert result.removed_count == 2


# ---------------------------------------------------------------------------
# Semantic duplicates (normalisation)
# ---------------------------------------------------------------------------

def test_semantic_duplicates_deduplicated():
    # "*/1" and "*" are semantically equivalent
    result = deduplicate(["*/1 * * * *", "* * * * *"])
    assert result.kept_count == 1
    assert result.removed_count == 1


# ---------------------------------------------------------------------------
# Labels
# ---------------------------------------------------------------------------

def test_labels_propagated_to_entries():
    result = deduplicate(["0 9 * * *", "0 17 * * *"], labels=["morning", "evening"])
    assert result.entries[0].label == "morning"
    assert result.entries[1].label == "evening"


def test_none_label_allowed():
    result = deduplicate(["0 0 * * *"], labels=[None])
    assert result.entries[0].label is None


def test_label_length_mismatch_raises():
    with pytest.raises(ValueError):
        deduplicate(["* * * * *", "0 * * * *"], labels=["only-one"])


# ---------------------------------------------------------------------------
# Summary / __str__
# ---------------------------------------------------------------------------

def test_summary_contains_counts():
    result = deduplicate(["* * * * *", "* * * * *", "0 12 * * *"])
    s = result.summary
    assert "2" in s  # kept
    assert "1" in s  # removed


def test_str_result_equals_summary():
    result = deduplicate(["0 1 * * *"])
    assert str(result) == result.summary


def test_entry_str_shows_expression():
    result = deduplicate(["0 8 * * *"])
    assert "0 8 * * *" in str(result.entries[0])


def test_entry_str_shows_label_when_present():
    result = deduplicate(["0 8 * * *"], labels=["standup"])
    assert "standup" in str(result.entries[0])


def test_entry_str_shows_duplicate_count():
    result = deduplicate(["0 8 * * *", "0 8 * * *"])
    assert "duplicate" in str(result.entries[0])


# ---------------------------------------------------------------------------
# Empty input
# ---------------------------------------------------------------------------

def test_empty_list_returns_empty_result():
    result = deduplicate([])
    assert result.kept_count == 0
    assert result.removed_count == 0
    assert result.original_count == 0
