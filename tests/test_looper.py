"""Tests for cronparse.looper."""
from datetime import datetime, timezone

import pytest

from cronparse.looper import LoopResult, LoopCycle, loop, _detect_cycle


def dt(*args):
    return datetime(*args, tzinfo=timezone.utc)


START = dt(2024, 1, 15, 12, 0)


def test_loop_returns_loop_result():
    result = loop("* * * * *", START)
    assert isinstance(result, LoopResult)


def test_loop_stores_expression():
    result = loop("*/5 * * * *", START)
    assert result.expression == "*/5 * * * *"


def test_loop_label_none_by_default():
    result = loop("* * * * *", START)
    assert result.label is None


def test_loop_label_propagated():
    result = loop("* * * * *", START, label="every-minute")
    assert result.label == "every-minute"


def test_loop_every_minute_has_cycle():
    result = loop("* * * * *", START, n=5)
    assert result.has_cycle is True


def test_loop_every_minute_period_is_one():
    result = loop("* * * * *", START, n=5)
    assert result.cycle is not None
    assert result.cycle.period_minutes == 1


def test_loop_step_five_period_is_five():
    result = loop("*/5 * * * *", START, n=6)
    assert result.cycle is not None
    assert result.cycle.period_minutes == 5


def test_loop_hourly_period_is_sixty():
    result = loop("0 * * * *", START, n=4)
    assert result.cycle is not None
    assert result.cycle.period_minutes == 60


def test_loop_runs_count_matches_n():
    result = loop("* * * * *", START, n=8)
    assert len(result.runs) == 8


def test_loop_cycle_occurrences_matches_runs():
    result = loop("*/10 * * * *", START, n=5)
    assert result.cycle is not None
    assert result.cycle.occurrences == 5


def test_loop_cycle_first_and_last():
    result = loop("*/15 * * * *", START, n=4)
    assert result.cycle is not None
    assert result.cycle.first == result.runs[0]
    assert result.cycle.last == result.runs[-1]


def test_loop_summary_contains_expression():
    result = loop("* * * * *", START, n=3)
    assert "* * * * *" in result.summary


def test_loop_summary_with_cycle_mentions_period():
    result = loop("*/5 * * * *", START, n=4)
    assert "5" in result.summary


def test_loop_str_equals_summary():
    result = loop("0 * * * *", START, n=3)
    assert str(result) == result.summary


def test_detect_cycle_uniform_gaps_returns_cycle():
    runs = [
        dt(2024, 1, 1, 0, i)
        for i in range(5)
    ]
    cycle = _detect_cycle(runs)
    assert cycle is not None
    assert cycle.period_minutes == 1


def test_detect_cycle_single_run_returns_none():
    cycle = _detect_cycle([dt(2024, 1, 1, 0, 0)])
    assert cycle is None


def test_detect_cycle_empty_returns_none():
    cycle = _detect_cycle([])
    assert cycle is None


def test_loop_cycle_str_contains_period():
    result = loop("*/30 * * * *", START, n=3)
    assert result.cycle is not None
    assert "30" in str(result.cycle)
