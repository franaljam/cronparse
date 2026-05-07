"""Tests for cronparse.pauser."""
from datetime import datetime, timezone

import pytest

from cronparse.pauser import PauseResult, pause, pause_many


def dt(year=2024, month=1, day=1, hour=0, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# pause() return type
# ---------------------------------------------------------------------------

def test_pause_returns_pause_result():
    result = pause("* * * * *", dt())
    assert isinstance(result, PauseResult)


def test_pause_stores_expression():
    result = pause("0 9 * * *", dt())
    assert result.expression == "0 9 * * *"


def test_pause_label_none_by_default():
    result = pause("* * * * *", dt())
    assert result.label is None


def test_pause_label_propagated():
    result = pause("* * * * *", dt(), label="my job")
    assert result.label == "my job"


def test_pause_anchor_stored():
    anchor = dt(hour=8)
    result = pause("* * * * *", anchor)
    assert result.anchor == anchor


# ---------------------------------------------------------------------------
# Skipped runs
# ---------------------------------------------------------------------------

def test_pause_default_skip_is_one():
    result = pause("* * * * *", dt())
    assert result.count() == 1


def test_pause_skip_two():
    result = pause("* * * * *", dt(), skip=2)
    assert result.count() == 2


def test_pause_skip_zero_no_skipped():
    result = pause("* * * * *", dt(), skip=0)
    assert result.count() == 0
    assert result.skipped == []


def test_pause_skipped_are_datetimes():
    result = pause("* * * * *", dt(), skip=3)
    for s in result.skipped:
        assert isinstance(s, datetime)


def test_pause_every_minute_skipped_is_one_minute_after_anchor():
    anchor = dt(hour=6, minute=0)
    result = pause("* * * * *", anchor, skip=1)
    assert result.skipped[0].minute == 1 or result.skipped[0].hour > 6


# ---------------------------------------------------------------------------
# Resumed run
# ---------------------------------------------------------------------------

def test_pause_resumed_at_is_datetime():
    result = pause("* * * * *", dt())
    assert isinstance(result.resumed_at, datetime)


def test_pause_resumed_at_after_last_skipped():
    result = pause("* * * * *", dt(), skip=2)
    assert result.resumed_at > result.skipped[-1]


def test_pause_skip_zero_resumed_is_first_run():
    result_zero = pause("* * * * *", dt(), skip=0)
    result_one = pause("* * * * *", dt(), skip=1)
    # When skip=0, resumed_at should equal the first skipped run of skip=1
    assert result_zero.resumed_at == result_one.skipped[0]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_pause_negative_skip_raises():
    with pytest.raises(ValueError, match="skip must be >= 0"):
        pause("* * * * *", dt(), skip=-1)


# ---------------------------------------------------------------------------
# __str__
# ---------------------------------------------------------------------------

def test_pause_str_contains_expression():
    result = pause("0 12 * * *", dt())
    assert "0 12 * * *" in str(result)


def test_pause_str_contains_skipped_count():
    result = pause("* * * * *", dt(), skip=2)
    assert "2" in str(result)


# ---------------------------------------------------------------------------
# pause_many
# ---------------------------------------------------------------------------

def test_pause_many_returns_list():
    results = pause_many(["* * * * *", "0 9 * * *"], dt())
    assert isinstance(results, list)
    assert len(results) == 2


def test_pause_many_all_pause_results():
    results = pause_many(["* * * * *", "0 9 * * *"], dt())
    for r in results:
        assert isinstance(r, PauseResult)


def test_pause_many_labels_propagated():
    results = pause_many(["* * * * *", "0 9 * * *"], dt(), labels=["a", "b"])
    assert results[0].label == "a"
    assert results[1].label == "b"


def test_pause_many_label_length_mismatch_raises():
    with pytest.raises(ValueError):
        pause_many(["* * * * *", "0 9 * * *"], dt(), labels=["only_one"])
