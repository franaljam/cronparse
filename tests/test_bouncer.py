"""Tests for cronparse.bouncer."""

from datetime import datetime, timedelta

import pytest

from cronparse.bouncer import BounceResult, bounce, bounce_many


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def dt(hour: int = 12, minute: int = 0) -> datetime:
    return datetime(2024, 6, 15, hour, minute, 0)


START = dt(12, 0)
END = dt(13, 0)  # one-hour window


# ---------------------------------------------------------------------------
# bounce()
# ---------------------------------------------------------------------------

def test_bounce_returns_bounce_result():
    result = bounce("* * * * *", START, END)
    assert isinstance(result, BounceResult)


def test_bounce_every_minute_fires():
    result = bounce("* * * * *", START, END)
    assert result.fires is True


def test_bounce_every_minute_first_hit_is_start():
    result = bounce("* * * * *", START, END)
    assert result.first_hit == START


def test_bounce_specific_time_inside_window_fires():
    result = bounce("30 12 * * *", START, END)
    assert result.fires is True
    assert result.first_hit == dt(12, 30)


def test_bounce_specific_time_outside_window_does_not_fire():
    result = bounce("0 15 * * *", START, END)
    assert result.fires is False
    assert result.first_hit is None


def test_bounce_stores_expression():
    result = bounce("0 9 * * *", START, END)
    assert result.expression == "0 9 * * *"


def test_bounce_stores_start_and_end():
    result = bounce("* * * * *", START, END)
    assert result.start == START
    assert result.end == END


def test_bounce_label_none_by_default():
    result = bounce("* * * * *", START, END)
    assert result.label is None


def test_bounce_label_propagated():
    result = bounce("* * * * *", START, END, label="heartbeat")
    assert result.label == "heartbeat"


def test_bounce_str_fires():
    result = bounce("* * * * *", START, END)
    assert "fires" in str(result)


def test_bounce_str_does_not_fire():
    result = bounce("0 23 * * *", START, END)
    assert "does not fire" in str(result)


def test_bounce_str_includes_label():
    result = bounce("* * * * *", START, END, label="job")
    assert "[job]" in str(result)


def test_bounce_minutes_until_first_every_minute():
    result = bounce("* * * * *", START, END)
    assert result.minutes_until_first == 0.0


def test_bounce_minutes_until_first_none_when_no_fire():
    result = bounce("0 23 * * *", START, END)
    assert result.minutes_until_first is None


def test_bounce_minutes_until_first_half_hour():
    result = bounce("30 12 * * *", START, END)
    assert result.minutes_until_first == 30.0


def test_bounce_invalid_window_raises():
    with pytest.raises(ValueError, match="end must be after start"):
        bounce("* * * * *", END, START)


# ---------------------------------------------------------------------------
# bounce_many()
# ---------------------------------------------------------------------------

def test_bounce_many_returns_list():
    results = bounce_many(["* * * * *", "0 9 * * *"], START, END)
    assert isinstance(results, list)
    assert len(results) == 2


def test_bounce_many_all_are_bounce_results():
    results = bounce_many(["* * * * *", "0 23 * * *"], START, END)
    assert all(isinstance(r, BounceResult) for r in results)


def test_bounce_many_labels_propagated():
    results = bounce_many(["* * * * *"], START, END, labels=["tick"])
    assert results[0].label == "tick"


def test_bounce_many_label_mismatch_raises():
    with pytest.raises(ValueError, match="labels length"):
        bounce_many(["* * * * *", "0 9 * * *"], START, END, labels=["only-one"])
