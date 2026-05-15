"""Tests for cronparse.freezer."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from cronparse.freezer import FreezeResult, freeze, freeze_many


def dt(minute: int = 0, hour: int = 0) -> datetime:
    return datetime(2024, 1, 15, hour, minute, 0, tzinfo=timezone.utc)


def test_freeze_returns_freeze_result():
    result = freeze("* * * * *", anchor=dt())
    assert isinstance(result, FreezeResult)


def test_freeze_stores_expression():
    result = freeze("0 * * * *", anchor=dt())
    assert result.expression == "0 * * * *"


def test_freeze_label_none_by_default():
    result = freeze("* * * * *", anchor=dt())
    assert result.label is None


def test_freeze_label_propagated():
    result = freeze("* * * * *", anchor=dt(), label="my-job")
    assert result.label == "my-job"


def test_freeze_skipped_count_matches_skip():
    result = freeze("* * * * *", anchor=dt(), skip=3, n=5)
    assert result.skipped == 3


def test_freeze_runs_after_resume_count_equals_n():
    result = freeze("* * * * *", anchor=dt(), skip=2, n=5)
    assert result.count == 5


def test_freeze_skip_zero_skips_nothing():
    result = freeze("* * * * *", anchor=dt(), skip=0, n=3)
    assert result.skipped == 0
    assert result.count == 3


def test_freeze_resume_at_is_datetime():
    result = freeze("* * * * *", anchor=dt(), skip=1, n=3)
    assert isinstance(result.resume_at, datetime)


def test_freeze_resume_at_is_first_run_after_skip():
    result = freeze("* * * * *", anchor=dt(0, 0), skip=2, n=3)
    assert result.resume_at == result.runs_after_resume[0]


def test_freeze_runs_are_datetimes():
    result = freeze("* * * * *", anchor=dt(), skip=1, n=4)
    assert all(isinstance(r, datetime) for r in result.runs_after_resume)


def test_freeze_runs_are_ascending():
    result = freeze("* * * * *", anchor=dt(), skip=1, n=5)
    runs = result.runs_after_resume
    assert runs == sorted(runs)


def test_freeze_first_and_last_properties():
    result = freeze("* * * * *", anchor=dt(), skip=0, n=3)
    assert result.first == result.runs_after_resume[0]
    assert result.last == result.runs_after_resume[-1]


def test_freeze_first_none_when_n_zero():
    result = freeze("* * * * *", anchor=dt(), skip=0, n=0)
    assert result.first is None
    assert result.last is None


def test_freeze_negative_skip_raises():
    with pytest.raises(ValueError, match="skip"):
        freeze("* * * * *", anchor=dt(), skip=-1)


def test_freeze_negative_n_raises():
    with pytest.raises(ValueError, match="n"):
        freeze("* * * * *", anchor=dt(), n=-1)


def test_freeze_str_contains_expression():
    result = freeze("0 9 * * 1", anchor=dt(), skip=1, n=2)
    assert "0 9 * * 1" in str(result)


def test_freeze_str_contains_skipped():
    result = freeze("* * * * *", anchor=dt(), skip=3, n=2)
    assert "skipped=3" in str(result)


def test_freeze_many_returns_list():
    results = freeze_many(["* * * * *", "0 * * * *"], anchor=dt())
    assert isinstance(results, list)
    assert len(results) == 2


def test_freeze_many_label_mismatch_raises():
    with pytest.raises(ValueError, match="labels"):
        freeze_many(["* * * * *", "0 * * * *"], anchor=dt(), labels=["only-one"])


def test_freeze_many_labels_propagated():
    results = freeze_many(
        ["* * * * *", "0 * * * *"],
        anchor=dt(),
        labels=["a", "b"],
    )
    assert results[0].label == "a"
    assert results[1].label == "b"
