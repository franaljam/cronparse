"""Tests for cronparse.splitter."""

import pytest
from cronparse.splitter import split, SplitResult, SplitField, FIELD_NAMES


def test_split_returns_split_result():
    result = split("* * * * *")
    assert isinstance(result, SplitResult)


def test_split_stores_expression():
    result = split("0 9 * * 1")
    assert result.expression == "0 9 * * 1"


def test_split_label_none_by_default():
    result = split("* * * * *")
    assert result.label is None


def test_split_label_propagated():
    result = split("0 6 * * *", label="Morning")
    assert result.label == "Morning"


def test_split_produces_five_fields():
    result = split("* * * * *")
    assert len(result.fields) == 5


def test_split_field_names_match_expected():
    result = split("* * * * *")
    names = [f.name for f in result.fields]
    assert names == FIELD_NAMES


def test_split_fields_are_split_field_instances():
    result = split("* * * * *")
    for field in result.fields:
        assert isinstance(field, SplitField)


def test_split_wildcard_all_fields_are_wildcard():
    result = split("* * * * *")
    assert all(f.is_wildcard for f in result.fields)


def test_split_specific_minute_not_wildcard():
    result = split("30 * * * *")
    minute = result.get("minute")
    assert minute is not None
    assert not minute.is_wildcard


def test_split_specific_minute_values():
    result = split("15 * * * *")
    minute = result.get("minute")
    assert minute.values == [15]


def test_split_range_field_values():
    result = split("0-4 * * * *")
    minute = result.get("minute")
    assert minute.values == [0, 1, 2, 3, 4]


def test_split_step_field_values():
    result = split("*/15 * * * *")
    minute = result.get("minute")
    assert set(minute.values) == {0, 15, 30, 45}


def test_split_get_returns_none_for_unknown():
    result = split("* * * * *")
    assert result.get("nonexistent") is None


def test_split_wildcard_fields_all_wildcard():
    result = split("* * * * *")
    assert result.wildcard_fields() == FIELD_NAMES


def test_split_wildcard_fields_partial():
    result = split("0 9 * * *")
    wildcards = result.wildcard_fields()
    assert "minute" not in wildcards
    assert "hour" not in wildcards
    assert "dom" in wildcards


def test_split_field_raw_preserved():
    result = split("*/5 12 * * 1-5")
    assert result.get("minute").raw == "*/5"
    assert result.get("hour").raw == "12"
    assert result.get("dow").raw == "1-5"


def test_split_summary_contains_expression():
    result = split("0 0 * * *", label="Midnight")
    summary = result.summary()
    assert "0 0 * * *" in summary
    assert "Midnight" in summary


def test_split_field_str_includes_label():
    result = split("* * * * *")
    minute = result.get("minute")
    assert "Minute" in str(minute)
    assert "wildcard" in str(minute)


def test_split_non_wildcard_field_str_no_wildcard_marker():
    result = split("30 * * * *")
    minute = result.get("minute")
    assert "wildcard" not in str(minute)
