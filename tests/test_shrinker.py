"""Tests for cronparse.shrinker."""

import pytest
from cronparse.shrinker import shrink, ShrinkResult


def test_shrink_returns_shrink_result():
    result = shrink("* * * * *")
    assert isinstance(result, ShrinkResult)


def test_shrink_stores_original_expression():
    result = shrink("* * * * *")
    assert result.original == "* * * * *"


def test_shrink_label_none_by_default():
    result = shrink("* * * * *")
    assert result.label is None


def test_shrink_label_propagated():
    result = shrink("* * * * *", label="my-job")
    assert result.label == "my-job"


def test_shrink_wildcard_expression_no_changes():
    result = shrink("* * * * *")
    assert not result.was_modified
    assert result.changed_fields == []


def test_shrink_step_of_one_minute_becomes_wildcard():
    result = shrink("*/1 * * * *")
    assert result.fields["minute"] == "*"
    assert "minute" in result.changed_fields


def test_shrink_step_of_one_hour_becomes_wildcard():
    result = shrink("* */1 * * *")
    assert result.fields["hour"] == "*"
    assert "minute" not in result.changed_fields
    assert "hour" in result.changed_fields


def test_shrink_range_covering_full_minute_span():
    result = shrink("0-59 * * * *")
    assert result.fields["minute"] == "*"
    assert "minute" in result.changed_fields


def test_shrink_range_covering_full_hour_span():
    result = shrink("* 0-23 * * *")
    assert result.fields["hour"] == "*"
    assert "hour" in result.changed_fields


def test_shrink_partial_range_not_changed():
    result = shrink("0-30 * * * *")
    assert result.fields["minute"] == "0-30"
    assert "minute" not in result.changed_fields


def test_shrink_specific_value_not_changed():
    result = shrink("5 3 * * *")
    assert result.fields["minute"] == "5"
    assert result.fields["hour"] == "3"
    assert not result.was_modified


def test_shrink_was_modified_true_when_changed():
    result = shrink("*/1 * * * *")
    assert result.was_modified


def test_shrink_str_includes_expression():
    result = shrink("*/1 * * * *")
    assert "* * * * *" in str(result)


def test_shrink_str_includes_label():
    result = shrink("* * * * *", label="job")
    assert "job" in str(result)


def test_shrink_summary_no_changes():
    result = shrink("* * * * *")
    assert "No changes" in result.summary


def test_shrink_summary_with_changes():
    result = shrink("*/1 * * * *")
    assert "->" in result.summary
    assert "minute" in result.summary


def test_shrink_expression_field_reconstructed():
    result = shrink("*/1 */1 * * *")
    assert result.expression == "* * * * *"


def test_shrink_step_two_not_changed():
    result = shrink("*/2 * * * *")
    assert result.fields["minute"] == "*/2"
    assert "minute" not in result.changed_fields
