"""Tests for cronparse.tracer."""

from datetime import datetime, timezone

import pytest

from cronparse.tracer import TraceStep, TraceResult, trace


@pytest.fixture()
def start() -> datetime:
    return datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)


def test_trace_returns_trace_result(start):
    result = trace("* * * * *", start, n=3)
    assert isinstance(result, TraceResult)


def test_trace_correct_step_count(start):
    result = trace("* * * * *", start, n=5)
    assert result.count == 5


def test_trace_steps_are_trace_step_instances(start):
    result = trace("* * * * *", start, n=2)
    for step in result.steps:
        assert isinstance(step, TraceStep)


def test_trace_index_starts_at_one(start):
    result = trace("* * * * *", start, n=3)
    assert result.steps[0].index == 1
    assert result.steps[1].index == 2
    assert result.steps[2].index == 3


def test_trace_stores_expression(start):
    result = trace("0 9 * * 1", start, n=1)
    assert result.expression == "0 9 * * 1"


def test_trace_label_propagated(start):
    result = trace("* * * * *", start, n=1, label="job-A")
    assert result.label == "job-A"
    assert result.steps[0].label == "job-A"


def test_trace_label_none_by_default(start):
    result = trace("* * * * *", start, n=1)
    assert result.label is None
    assert result.steps[0].label is None


def test_trace_matched_fields_is_dict(start):
    result = trace("* * * * *", start, n=1)
    assert isinstance(result.steps[0].matched_fields, dict)


def test_trace_matched_fields_contain_minute(start):
    result = trace("* * * * *", start, n=1)
    assert "minute" in result.steps[0].matched_fields


def test_trace_every_minute_dt_increments(start):
    result = trace("* * * * *", start, n=3)
    dts = [s.dt for s in result.steps]
    assert dts[1] > dts[0]
    assert dts[2] > dts[1]


def test_trace_step_str_contains_index(start):
    result = trace("* * * * *", start, n=1)
    assert "#1" in str(result.steps[0])


def test_trace_step_str_contains_label(start):
    result = trace("* * * * *", start, n=1, label="my-job")
    assert "my-job" in str(result.steps[0])


def test_trace_summary_contains_expression(start):
    result = trace("*/5 * * * *", start, n=2)
    summary = result.summary()
    assert "*/5 * * * *" in summary


def test_trace_summary_contains_all_steps(start):
    result = trace("* * * * *", start, n=3)
    summary = result.summary()
    assert "#1" in summary
    assert "#2" in summary
    assert "#3" in summary


def test_trace_n_zero_returns_empty(start):
    result = trace("* * * * *", start, n=0)
    assert result.count == 0
    assert result.steps == []
