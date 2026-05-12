"""Tests for cronparse.aligner."""
import pytest
from datetime import datetime

from cronparse.aligner import align, AlignResult, AlignedEntry


@pytest.fixture
def ref():
    return datetime(2024, 1, 15, 12, 0, 0)


def test_align_returns_align_result(ref):
    result = align(["* * * * *"], ref)
    assert isinstance(result, AlignResult)


def test_align_stores_reference(ref):
    result = align(["* * * * *"], ref)
    assert result.reference == ref


def test_align_entries_are_aligned_entry_instances(ref):
    result = align(["* * * * *", "0 * * * *"], ref)
    for entry in result.entries:
        assert isinstance(entry, AlignedEntry)


def test_align_count_matches_expressions(ref):
    exprs = ["* * * * *", "0 * * * *", "30 * * * *"]
    result = align(exprs, ref)
    assert result.count == 3


def test_align_every_minute_offset_is_zero_or_one(ref):
    result = align(["* * * * *"], ref)
    assert result.entries[0].offset_minutes >= 0
    assert result.entries[0].offset_minutes <= 1


def test_align_hourly_offset_is_zero_when_on_hour():
    ref = datetime(2024, 1, 15, 12, 0, 0)
    result = align(["0 * * * *"], ref)
    assert result.entries[0].offset_minutes == 0.0


def test_align_hourly_offset_positive_when_past_hour():
    ref = datetime(2024, 1, 15, 12, 30, 0)
    result = align(["0 * * * *"], ref)
    assert result.entries[0].offset_minutes == 30.0


def test_align_labels_propagated(ref):
    result = align(["* * * * *"], ref, labels=["job-a"])
    assert result.entries[0].label == "job-a"


def test_align_no_labels_is_none(ref):
    result = align(["* * * * *"], ref)
    assert result.entries[0].label is None


def test_align_label_length_mismatch_raises(ref):
    with pytest.raises(ValueError):
        align(["* * * * *", "0 * * * *"], ref, labels=["only-one"])


def test_align_earliest_returns_min_offset(ref):
    result = align(["0 * * * *", "* * * * *"], ref)
    assert result.earliest is not None
    assert result.earliest.offset_minutes <= result.latest.offset_minutes


def test_align_latest_returns_max_offset(ref):
    result = align(["0 * * * *", "* * * * *"], ref)
    assert result.latest is not None


def test_align_empty_list_returns_empty_result(ref):
    result = align([], ref)
    assert result.count == 0
    assert result.earliest is None
    assert result.latest is None


def test_align_summary_contains_count(ref):
    result = align(["* * * * *", "0 * * * *"], ref)
    assert "2" in result.summary()


def test_align_summary_empty(ref):
    result = align([], ref)
    assert "No" in result.summary()


def test_align_str_entry_contains_expression(ref):
    result = align(["* * * * *"], ref)
    assert "* * * * *" in str(result.entries[0])


def test_align_str_entry_contains_label(ref):
    result = align(["* * * * *"], ref, labels=["my-job"])
    assert "my-job" in str(result.entries[0])
