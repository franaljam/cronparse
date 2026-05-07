"""Tests for cronparse.rewinder."""

from datetime import datetime, timedelta

import pytest

from cronparse.rewinder import RewindResult, rewind


def dt(minute: int = 0, hour: int = 12, day: int = 15) -> datetime:
    return datetime(2024, 6, day, hour, minute, 0)


def test_rewind_returns_rewind_result():
    result = rewind("* * * * *", before=dt(), n=3)
    assert isinstance(result, RewindResult)


def test_rewind_correct_count():
    result = rewind("* * * * *", before=dt(), n=5)
    assert result.count == 5


def test_rewind_every_minute_all_before_anchor():
    anchor = dt(minute=30, hour=10)
    result = rewind("* * * * *", before=anchor, n=5)
    for run in result.runs:
        assert run < anchor


def test_rewind_every_minute_descending_order():
    anchor = dt(minute=30, hour=10)
    result = rewind("* * * * *", before=anchor, n=5)
    assert result.runs == sorted(result.runs, reverse=True)


def test_rewind_every_minute_consecutive():
    anchor = dt(minute=10, hour=8)
    result = rewind("* * * * *", before=anchor, n=3)
    for i in range(len(result.runs) - 1):
        diff = result.runs[i] - result.runs[i + 1]
        assert diff == timedelta(minutes=1)


def test_rewind_specific_hour_only_that_hour():
    anchor = datetime(2024, 6, 15, 14, 0, 0)
    result = rewind("0 9 * * *", before=anchor, n=3)
    for run in result.runs:
        assert run.hour == 9
        assert run.minute == 0


def test_rewind_label_stored():
    result = rewind("* * * * *", before=dt(), n=2, label="my-job")
    assert result.label == "my-job"


def test_rewind_no_label_is_none():
    result = rewind("* * * * *", before=dt(), n=2)
    assert result.label is None


def test_rewind_expression_stored():
    expr = "0 * * * *"
    result = rewind(expr, before=dt(), n=2)
    assert result.expression == expr


def test_rewind_latest_is_most_recent():
    anchor = dt(minute=30, hour=10)
    result = rewind("* * * * *", before=anchor, n=5)
    assert result.latest == result.runs[0]


def test_rewind_earliest_is_oldest():
    anchor = dt(minute=30, hour=10)
    result = rewind("* * * * *", before=anchor, n=5)
    assert result.earliest == result.runs[-1]


def test_rewind_invalid_n_raises():
    with pytest.raises(ValueError):
        rewind("* * * * *", before=dt(), n=0)


def test_rewind_str_contains_expression():
    result = rewind("* * * * *", before=dt(), n=2)
    assert "* * * * *" in str(result)


def test_rewind_str_contains_count():
    result = rewind("* * * * *", before=dt(), n=4)
    assert "4" in str(result)
