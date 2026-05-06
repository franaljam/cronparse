"""Tests for cronparse.normalizer."""

from __future__ import annotations

import pytest

from cronparse.normalizer import NormalizedExpression, normalize, are_equivalent


# ---------------------------------------------------------------------------
# normalize()
# ---------------------------------------------------------------------------

def test_normalize_returns_normalized_expression():
    result = normalize("* * * * *")
    assert isinstance(result, NormalizedExpression)


def test_normalize_wildcard_stays_wildcard():
    result = normalize("* * * * *")
    assert result.canonical == "* * * * *"


def test_normalize_specific_values():
    result = normalize("30 9 * * *")
    assert result.canonical == "30 9 * * *"


def test_normalize_range_preserved():
    result = normalize("0-5 * * * *")
    assert result.canonical == "0-5 * * * *"


def test_normalize_step_preserved():
    result = normalize("*/15 * * * *")
    assert result.canonical == "*/15 * * * *"


def test_normalize_list_preserved():
    result = normalize("0,15,30,45 * * * *")
    assert result.canonical == "0,15,30,45 * * * *"


def test_normalize_alias_daily():
    result = normalize("@daily")
    assert result.was_alias is True
    assert result.canonical == "0 0 * * *"


def test_normalize_alias_hourly():
    result = normalize("@hourly")
    assert result.was_alias is True
    assert result.canonical == "0 * * * *"


def test_normalize_alias_weekly():
    result = normalize("@weekly")
    assert result.was_alias is True
    assert result.canonical == "0 0 * * 0"


def test_normalize_plain_expression_not_alias():
    result = normalize("0 0 * * *")
    assert result.was_alias is False


def test_normalize_original_preserved():
    result = normalize("@monthly")
    assert result.original == "@monthly"


def test_normalize_expression_object_attached():
    result = normalize("30 6 * * 1")
    assert 30 in result.expression.minute
    assert 6 in result.expression.hour


# ---------------------------------------------------------------------------
# are_equivalent()
# ---------------------------------------------------------------------------

def test_equivalent_identical_expressions():
    assert are_equivalent("0 0 * * *", "0 0 * * *") is True


def test_equivalent_alias_and_raw():
    assert are_equivalent("@daily", "0 0 * * *") is True


def test_equivalent_different_expressions():
    assert are_equivalent("*/5 * * * *", "*/10 * * * *") is False


def test_equivalent_two_aliases():
    assert are_equivalent("@hourly", "@hourly") is True


def test_not_equivalent_minute_differs():
    assert are_equivalent("0 12 * * *", "30 12 * * *") is False
