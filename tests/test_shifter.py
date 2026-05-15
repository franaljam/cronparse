"""Tests for cronparse.shifter."""
from __future__ import annotations

import pytest

from cronparse.shifter import ShiftResult, shift, shift_many, _shift_token


# ---------------------------------------------------------------------------
# _shift_token unit tests
# ---------------------------------------------------------------------------

def test_shift_token_wildcard_unchanged():
    assert _shift_token("*", 5, 0, 59) == "*"


def test_shift_token_plain_value():
    assert _shift_token("10", 5, 0, 59) == "15"


def test_shift_token_wraps_around():
    assert _shift_token("58", 5, 0, 59) == "3"


def test_shift_token_negative_offset():
    assert _shift_token("10", -5, 0, 59) == "5"


def test_shift_token_negative_wraps():
    assert _shift_token("2", -5, 0, 59) == "57"


def test_shift_token_list():
    result = _shift_token("0,30", 15, 0, 59)
    assert result == "15,45"


def test_shift_token_range():
    result = _shift_token("10-20", 5, 0, 59)
    assert result == "15-25"


def test_shift_token_step_with_base():
    result = _shift_token("0/15", 5, 0, 59)
    assert result == "5/15"


def test_shift_token_step_wildcard_base_unchanged():
    result = _shift_token("*/15", 5, 0, 59)
    assert result == "*/15"


# ---------------------------------------------------------------------------
# shift() tests
# ---------------------------------------------------------------------------

def test_shift_returns_shift_result():
    result = shift("0 * * * *", 15)
    assert isinstance(result, ShiftResult)


def test_shift_stores_original_expression():
    result = shift("0 * * * *", 15)
    assert result.original_expression == "0 * * * *"


def test_shift_label_none_by_default():
    result = shift("0 * * * *", 15)
    assert result.label is None


def test_shift_label_propagated():
    result = shift("0 * * * *", 15, label="hourly")
    assert result.label == "hourly"


def test_shift_zero_offset_no_modification():
    result = shift("5 * * * *", 0)
    assert not result.was_modified
    assert result.shifted_expression == "5 * * * *"


def test_shift_wildcard_minute_no_modification():
    result = shift("* * * * *", 10)
    assert not result.was_modified
    assert result.shifted_expression == "* * * * *"


def test_shift_specific_minute_changed():
    result = shift("0 * * * *", 15)
    assert result.was_modified
    assert result.shifted_expression == "15 * * * *"


def test_shift_wraps_correctly():
    result = shift("55 * * * *", 10)
    assert result.shifted_expression == "5 * * * *"


def test_shift_other_fields_preserved():
    result = shift("0 9 1 6 1", 30)
    parts = result.shifted_expression.split()
    assert parts[1:] == ["9", "1", "6", "1"]


def test_shift_offset_stored():
    result = shift("0 * * * *", 20)
    assert result.offset_minutes == 20


def test_shift_str_contains_arrow():
    result = shift("0 * * * *", 5)
    assert "->" in str(result)


def test_shift_summary_no_change():
    result = shift("0 * * * *", 0)
    assert "no change" in result.summary()


# ---------------------------------------------------------------------------
# shift_many() tests
# ---------------------------------------------------------------------------

def test_shift_many_returns_list():
    results = shift_many(["0 * * * *", "30 * * * *"], 15)
    assert isinstance(results, list)
    assert len(results) == 2


def test_shift_many_all_are_shift_results():
    results = shift_many(["0 * * * *", "30 * * * *"], 15)
    assert all(isinstance(r, ShiftResult) for r in results)


def test_shift_many_with_labels():
    results = shift_many(["0 * * * *", "30 * * * *"], 5, labels=["a", "b"])
    assert results[0].label == "a"
    assert results[1].label == "b"


def test_shift_many_label_mismatch_raises():
    with pytest.raises(ValueError):
        shift_many(["0 * * * *", "30 * * * *"], 5, labels=["only_one"])
