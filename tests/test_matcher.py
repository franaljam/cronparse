"""Tests for cronparse.matcher."""

from datetime import datetime

import pytest

from cronparse.matcher import FieldMatchResult, MatchResult, match, matches


@pytest.fixture
def monday_9am():
    # 2024-01-08 is a Monday; weekday() == 0
    return datetime(2024, 1, 8, 9, 30)


def test_match_returns_match_result(monday_9am):
    result = match("* * * * *", monday_9am)
    assert isinstance(result, MatchResult)


def test_wildcard_expression_always_matches(monday_9am):
    assert match("* * * * *", monday_9am).matched is True


def test_specific_minute_hour_matches(monday_9am):
    result = match("30 9 * * *", monday_9am)
    assert result.matched is True


def test_specific_minute_wrong_does_not_match(monday_9am):
    result = match("15 9 * * *", monday_9am)
    assert result.matched is False


def test_match_result_has_five_fields(monday_9am):
    result = match("* * * * *", monday_9am)
    assert len(result.fields) == 5


def test_field_match_result_type(monday_9am):
    result = match("* * * * *", monday_9am)
    for f in result.fields:
        assert isinstance(f, FieldMatchResult)


def test_failed_fields_empty_when_all_match(monday_9am):
    result = match("* * * * *", monday_9am)
    assert result.failed_fields == []


def test_failed_fields_populated_on_mismatch(monday_9am):
    result = match("0 0 * * *", monday_9am)
    failed_names = [f.field_name for f in result.failed_fields]
    assert "minute" in failed_names
    assert "hour" in failed_names


def test_summary_contains_match_status(monday_9am):
    result = match("30 9 * * *", monday_9am)
    assert "MATCH" in result.summary()


def test_summary_contains_no_match_status(monday_9am):
    result = match("0 0 * * *", monday_9am)
    assert "NO MATCH" in result.summary()


def test_summary_contains_expression(monday_9am):
    result = match("30 9 * * *", monday_9am)
    assert "30 9 * * *" in result.summary()


def test_matches_shorthand_true(monday_9am):
    assert matches("30 9 * * *", monday_9am) is True


def test_matches_shorthand_false(monday_9am):
    assert matches("0 0 * * *", monday_9am) is False


def test_field_match_result_str_contains_checkmark():
    fr = FieldMatchResult(field_name="minute", value=30, allowed=[30], matched=True)
    assert "✓" in str(fr)


def test_field_match_result_str_contains_cross():
    fr = FieldMatchResult(field_name="minute", value=15, allowed=[30], matched=False)
    assert "✗" in str(fr)


def test_step_expression_matches_correct_minutes():
    # */15 matches 0, 15, 30, 45
    dt_match = datetime(2024, 1, 8, 9, 15)
    dt_no_match = datetime(2024, 1, 8, 9, 7)
    assert matches("*/15 * * * *", dt_match) is True
    assert matches("*/15 * * * *", dt_no_match) is False


def test_match_stores_expression_string(monday_9am):
    result = match("30 9 * * *", monday_9am)
    assert result.expression == "30 9 * * *"


def test_match_stores_datetime(monday_9am):
    result = match("* * * * *", monday_9am)
    assert result.dt == monday_9am
