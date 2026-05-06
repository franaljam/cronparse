"""Tests for cronparse.segmenter."""

import pytest
from cronparse.segmenter import segment, SegmentResult, SegmentEntry, _classify_segment


def test_segment_returns_segment_result():
    result = segment(["* * * * *"])
    assert isinstance(result, SegmentResult)


def test_segment_every_minute_is_minutely():
    result = segment(["* * * * *"])
    assert len(result.buckets["minutely"]) == 1


def test_segment_hourly_expression():
    result = segment(["0 * * * *"])
    assert len(result.buckets["hourly"]) == 1


def test_segment_daily_expression():
    result = segment(["0 9 * * *"])
    assert len(result.buckets["daily"]) == 1


def test_segment_entry_type():
    result = segment(["0 9 * * *"])
    entry = result.buckets["daily"][0]
    assert isinstance(entry, SegmentEntry)


def test_segment_entry_stores_expression():
    result = segment(["0 9 * * *"])
    entry = result.buckets["daily"][0]
    assert entry.expression == "0 9 * * *"


def test_segment_entry_label_none_by_default():
    result = segment(["0 9 * * *"])
    entry = result.buckets["daily"][0]
    assert entry.label is None


def test_segment_entry_label_propagated():
    result = segment(["0 9 * * *"], labels=["morning"])
    entry = result.buckets["daily"][0]
    assert entry.label == "morning"


def test_segment_label_length_mismatch_raises():
    with pytest.raises(ValueError):
        segment(["0 9 * * *", "* * * * *"], labels=["only-one"])


def test_segment_multiple_expressions():
    result = segment(["* * * * *", "0 9 * * *"])
    all_entries = result.all_entries()
    assert len(all_entries) == 2


def test_segment_all_entries_returns_flat_list():
    result = segment(["* * * * *", "0 * * * *", "0 9 * * *"])
    assert len(result.all_entries()) == 3


def test_segment_summary_contains_bucket_names():
    result = segment(["* * * * *", "0 9 * * *"])
    s = result.summary()
    assert "minutely" in s
    assert "daily" in s


def test_segment_empty_list_summary():
    result = segment([])
    assert result.summary() == "No expressions segmented."


def test_classify_segment_minutely():
    assert _classify_segment(1440) == "minutely"


def test_classify_segment_hourly():
    assert _classify_segment(24) == "hourly"


def test_classify_segment_daily():
    assert _classify_segment(1) == "daily"


def test_classify_segment_rarely():
    assert _classify_segment(0.001) == "rarely"


def test_segment_entry_str_contains_expression():
    result = segment(["0 9 * * *"], labels=["job"])
    entry = result.buckets["daily"][0]
    s = str(entry)
    assert "0 9 * * *" in s
    assert "job" in s
    assert "daily" in s
