"""Integration tests for looper with parser and scheduler."""
from datetime import datetime, timezone

import pytest

from cronparse.looper import loop
from cronparse.parser import parse
from cronparse.humanizer import humanize


def dt(*args):
    return datetime(*args, tzinfo=timezone.utc)


START = dt(2024, 3, 1, 8, 0)


def test_loop_expression_is_parseable():
    result = loop("*/10 * * * *", START, n=6)
    expr = parse(result.expression)
    assert expr is not None


def test_loop_expression_humanizable():
    result = loop("0 9 * * *", START, n=5)
    text = humanize(parse(result.expression))
    assert isinstance(text, str)
    assert len(text) > 0


def test_loop_runs_are_datetimes():
    result = loop("*/15 * * * *", START, n=4)
    for r in result.runs:
        assert isinstance(r, datetime)


def test_loop_runs_are_ascending():
    result = loop("* * * * *", START, n=10)
    for i in range(len(result.runs) - 1):
        assert result.runs[i] < result.runs[i + 1]


def test_loop_every_minute_cycle_period_one():
    result = loop("* * * * *", START, n=10)
    assert result.cycle is not None
    assert result.cycle.period_minutes == 1


def test_loop_step_30_period_is_30():
    result = loop("*/30 * * * *", START, n=4)
    assert result.cycle is not None
    assert result.cycle.period_minutes == 30


def test_loop_daily_period_is_1440():
    result = loop("0 0 * * *", START, n=3)
    assert result.cycle is not None
    assert result.cycle.period_minutes == 1440


def test_loop_cycle_first_before_last():
    result = loop("*/5 * * * *", START, n=5)
    assert result.cycle is not None
    assert result.cycle.first < result.cycle.last
