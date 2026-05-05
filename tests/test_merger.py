"""Tests for cronparse.merger module."""

import pytest
from cronparse.merger import merge, MergeResult


def test_merge_returns_merge_result():
    result = merge(["* * * * *", "0 * * * *"])
    assert isinstance(result, MergeResult)


def test_merge_empty_list_returns_empty_result():
    result = merge([])
    assert result.expressions == []
    assert result.merged_fields == {}
    assert result.labels == []


def test_merge_assigns_default_labels():
    result = merge(["* * * * *", "0 0 * * *"])
    assert result.labels == ["expr_0", "expr_1"]


def test_merge_custom_labels():
    result = merge(["* * * * *", "0 0 * * *"], labels=["job_a", "job_b"])
    assert result.labels == ["job_a", "job_b"]


def test_merge_label_length_mismatch_raises():
    with pytest.raises(ValueError):
        merge(["* * * * *", "0 0 * * *"], labels=["only_one"])


def test_merge_all_minutes_union():
    result = merge(["0 * * * *", "30 * * * *"])
    assert 0 in result.all_minutes()
    assert 30 in result.all_minutes()


def test_merge_all_hours_union():
    result = merge(["0 6 * * *", "0 18 * * *"])
    assert 6 in result.all_hours()
    assert 18 in result.all_hours()


def test_merge_common_minutes_intersection():
    result = merge(["0,30 * * * *", "0,15 * * * *"])
    common = result.common_minutes()
    assert 0 in common
    assert 30 not in common
    assert 15 not in common


def test_merge_common_hours_intersection():
    result = merge(["0 6,12 * * *", "0 12,18 * * *"])
    common = result.common_hours()
    assert 12 in common
    assert 6 not in common
    assert 18 not in common


def test_merge_common_minutes_empty_when_no_overlap():
    result = merge(["0 * * * *", "30 * * * *"])
    assert result.common_minutes() == set()


def test_merge_wildcard_includes_all_values():
    result = merge(["* * * * *"])
    assert len(result.all_minutes()) == 60
    assert len(result.all_hours()) == 24


def test_merge_human_summary_contains_labels():
    result = merge(["0 9 * * 1"], labels=["morning_job"])
    summary = result.human_summary()
    assert "morning_job" in summary


def test_merge_human_summary_empty():
    result = merge([])
    assert result.human_summary() == "No expressions"


def test_merge_merged_fields_keys():
    result = merge(["* * * * *"])
    assert set(result.merged_fields.keys()) == {"minute", "hour", "day", "month", "weekday"}


def test_merge_single_expression_common_equals_all():
    result = merge(["0,15,30 * * * *"])
    assert result.common_minutes() == result.all_minutes()
