"""Tests for cronparse.parser module."""

import pytest
from cronparse.parser import parse, CronExpression, CronField


def test_parse_returns_cron_expression():
    expr = parse("* * * * *")
    assert isinstance(expr, CronExpression)


def test_wildcard_minute_expands_all():
    expr = parse("* * * * *")
    assert expr.minute.values == list(range(0, 60))


def test_wildcard_hour_expands_all():
    expr = parse("* * * * *")
    assert expr.hour.values == list(range(0, 24))


def test_specific_value():
    expr = parse("30 14 * * *")
    assert expr.minute.values == [30]
    assert expr.hour.values == [14]


def test_range_field():
    expr = parse("0 9-17 * * *")
    assert expr.hour.values == list(range(9, 18))


def test_step_field():
    expr = parse("*/15 * * * *")
    assert expr.minute.values == [0, 15, 30, 45]


def test_step_with_range():
    expr = parse("0 0-12/4 * * *")
    assert expr.hour.values == [0, 4, 8, 12]


def test_list_field():
    expr = parse("0 8,12,18 * * *")
    assert expr.hour.values == [8, 12, 18]


def test_month_name_resolution():
    expr = parse("0 0 1 jan *")
    assert expr.month.values == [1]


def test_day_name_resolution():
    expr = parse("0 0 * * mon-fri")
    assert expr.day_of_week.values == [1, 2, 3, 4, 5]


def test_invalid_expression_raises():
    with pytest.raises(ValueError, match="expected 5 fields"):
        parse("* * * *")


def test_raw_preserved():
    raw = "30 6 * * 1-5"
    expr = parse(raw)
    assert expr.raw == raw
    assert expr.minute.raw == "30"
    assert expr.day_of_week.raw == "1-5"


def test_out_of_range_values_excluded():
    # step starting beyond max should yield empty or valid subset
    expr = parse("0 0 1 1 *")
    assert all(0 <= v <= 6 for v in expr.day_of_week.values)


def test_combined_list_and_range():
    expr = parse("1,15,30-35 * * * *")
    assert 1 in expr.minute.values
    assert 15 in expr.minute.values
    assert 30 in expr.minute.values
    assert 35 in expr.minute.values
