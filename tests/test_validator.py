"""Tests for cronparse.validator module."""

import pytest
from cronparse.validator import validate, ValidationResult, ValidationError


def test_valid_wildcard_expression():
    result = validate("* * * * *")
    assert result.valid is True
    assert result.errors == []


def test_valid_specific_values():
    result = validate("30 9 15 6 1")
    assert result.valid is True


def test_valid_range_expression():
    result = validate("0-30 8-18 * * 1-5")
    assert result.valid is True


def test_valid_step_expression():
    result = validate("*/5 */2 * * *")
    assert result.valid is True


def test_valid_list_expression():
    result = validate("0,15,30,45 * * * *")
    assert result.valid is True


def test_wrong_field_count_too_few():
    result = validate("* * * *")
    assert result.valid is False
    assert any("5 fields" in e.message for e in result.errors)


def test_wrong_field_count_too_many():
    result = validate("* * * * * *")
    assert result.valid is False


def test_minute_out_of_range():
    result = validate("60 * * * *")
    assert result.valid is False
    assert result.errors[0].field == "minute"
    assert "out of bounds" in result.errors[0].message


def test_hour_out_of_range():
    result = validate("* 24 * * *")
    assert result.valid is False
    assert result.errors[0].field == "hour"


def test_day_out_of_range_zero():
    result = validate("* * 0 * *")
    assert result.valid is False
    assert result.errors[0].field == "day"


def test_month_out_of_range():
    result = validate("* * * 13 *")
    assert result.valid is False
    assert result.errors[0].field == "month"


def test_invalid_range_start_greater_than_end():
    result = validate("30-10 * * * *")
    assert result.valid is False
    assert "greater than end" in result.errors[0].message


def test_invalid_step_zero():
    result = validate("*/0 * * * *")
    assert result.valid is False
    assert "step" in result.errors[0].message.lower()


def test_invalid_token():
    result = validate("abc * * * *")
    assert result.valid is False
    assert "Unrecognized token" in result.errors[0].message


def test_bool_conversion():
    assert bool(validate("* * * * *")) is True
    assert bool(validate("99 * * * *")) is False


def test_error_messages_returns_strings():
    result = validate("99 25 * * *")
    msgs = result.error_messages()
    assert all(isinstance(m, str) for m in msgs)
    assert len(msgs) == 2
