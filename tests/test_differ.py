"""Tests for cronparse.differ module."""

import pytest
from cronparse.differ import diff, diff_expressions, CronDiff, FieldDiff
from cronparse.parser import parse


def test_diff_identical_expressions_no_changes():
    result = diff("* * * * *", "* * * * *")
    assert isinstance(result, CronDiff)
    assert not result.has_changes


def test_diff_different_minute_detected():
    result = diff("0 * * * *", "30 * * * *")
    assert result.has_changes
    names = [d.field for d in result.field_diffs]
    assert "minute" in names


def test_diff_multiple_fields_changed():
    result = diff("0 0 * * *", "30 12 * * *")
    names = [d.field for d in result.field_diffs]
    assert "minute" in names
    assert "hour" in names


def test_diff_field_diff_added_removed():
    result = diff("0 * * * *", "0,30 * * * *")
    minute_diff = next(d for d in result.field_diffs if d.field == "minute")
    assert 30 in minute_diff.added
    assert not minute_diff.removed


def test_diff_field_diff_removed():
    result = diff("0,30 * * * *", "0 * * * *")
    minute_diff = next(d for d in result.field_diffs if d.field == "minute")
    assert 30 in minute_diff.removed
    assert not minute_diff.added


def test_diff_summary_equivalent():
    result = diff("* * * * *", "* * * * *")
    assert result.summary() == "Expressions are equivalent."


def test_diff_summary_contains_labels():
    result = diff("0 * * * *", "30 * * * *")
    summary = result.summary()
    assert "0 * * * *" in summary
    assert "30 * * * *" in summary


def test_diff_summary_contains_changes():
    result = diff("0 * * * *", "30 * * * *")
    summary = result.summary()
    assert "minute" in summary
    assert "Changes:" in summary


def test_diff_expressions_uses_parsed_objects():
    cron_a = parse("0 9 * * 1")
    cron_b = parse("0 9 * * 5")
    result = diff_expressions(cron_a, cron_b, "weekday-mon", "weekday-fri")
    names = [d.field for d in result.field_diffs]
    assert "day of week" in names
    assert result.left_expr == "weekday-mon"
    assert result.right_expr == "weekday-fri"


def test_field_diff_str_added():
    fd = FieldDiff("minute", frozenset({0}), frozenset({0, 30}), frozenset({30}), frozenset())
    assert "+" in str(fd)
    assert "30" in str(fd)


def test_field_diff_str_removed():
    fd = FieldDiff("hour", frozenset({0, 12}), frozenset({0}), frozenset(), frozenset({12}))
    assert "-" in str(fd)
    assert "12" in str(fd)


def test_diff_human_readable_populated():
    result = diff("0 9 * * *", "0 17 * * *")
    assert result.left_human
    assert result.right_human
    assert result.left_human != result.right_human
