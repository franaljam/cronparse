"""Tests for cronparse.trimmer."""

import pytest

from cronparse.trimmer import TrimResult, trim, trim_many


def test_trim_returns_trim_result():
    result = trim("* * * * *")
    assert isinstance(result, TrimResult)


def test_trim_stores_original_expression():
    result = trim("0 9 * * 1")
    assert result.original == "0 9 * * 1"


def test_trim_label_none_by_default():
    result = trim("* * * * *")
    assert result.label is None


def test_trim_label_propagated():
    result = trim("0 9 * * 1", label="morning")
    assert result.label == "morning"


def test_trim_wildcard_expression_no_changes():
    result = trim("* * * * *")
    assert result.was_modified is False
    assert result.change_count == 0


def test_trim_specific_values_no_changes():
    result = trim("0 9 * * 1")
    assert result.was_modified is False


def test_trim_was_modified_false_when_clean():
    result = trim("30 6 * * *")
    assert not result.was_modified


def test_trim_change_count_zero_when_clean():
    result = trim("0 0 1 1 0")
    assert result.change_count == 0


def test_trim_expression_field_present():
    result = trim("* * * * *")
    assert result.expression is not None
    assert len(result.expression.split()) == 5


def test_trim_trimmed_fields_empty_when_no_changes():
    result = trim("0 12 * * 5")
    assert result.trimmed_fields == []


def test_trim_str_no_changes():
    result = trim("0 9 * * 1")
    assert "no changes" in str(result)


def test_trim_str_with_changes_shows_arrow():
    # Build an expression where minute field covers full 0-59 range
    minutes = ",".join(str(i) for i in range(60))
    expr = f"{minutes} * * * *"
    result = trim(expr)
    if result.was_modified:
        assert "->" in str(result)


def test_trim_many_returns_list():
    results = trim_many(["* * * * *", "0 9 * * 1"])
    assert isinstance(results, list)
    assert len(results) == 2


def test_trim_many_all_trim_results():
    results = trim_many(["* * * * *", "0 9 * * 1"])
    assert all(isinstance(r, TrimResult) for r in results)


def test_trim_many_default_labels_are_none():
    results = trim_many(["* * * * *", "0 9 * * 1"])
    assert all(r.label is None for r in results)


def test_trim_many_custom_labels():
    results = trim_many(["* * * * *", "0 9 * * 1"], labels=["a", "b"])
    assert results[0].label == "a"
    assert results[1].label == "b"


def test_trim_many_label_length_mismatch_raises():
    with pytest.raises(ValueError):
        trim_many(["* * * * *", "0 9 * * 1"], labels=["only-one"])


def test_trim_full_minute_range_collapses():
    minutes = ",".join(str(i) for i in range(60))
    expr = f"{minutes} 0 * * *"
    result = trim(expr)
    assert result.expression.split()[0] == "*"


def test_trim_full_minute_range_adds_change():
    minutes = ",".join(str(i) for i in range(60))
    expr = f"{minutes} 0 * * *"
    result = trim(expr)
    assert result.was_modified
    assert "minute" in result.trimmed_fields
