"""Tests for cronparse.pinpointer."""

from datetime import datetime, timezone

import pytest

from cronparse.pinpointer import PinpointResult, pinpoint, pinpoint_many


@pytest.fixture()
def anchor() -> datetime:
    return datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)


def test_pinpoint_returns_pinpoint_result(anchor):
    result = pinpoint("* * * * *", anchor)
    assert isinstance(result, PinpointResult)


def test_pinpoint_every_minute_next_is_one_minute_later(anchor):
    result = pinpoint("* * * * *", anchor)
    assert result.target == datetime(2024, 1, 15, 12, 1, 0, tzinfo=timezone.utc)


def test_pinpoint_delta_seconds_every_minute(anchor):
    result = pinpoint("* * * * *", anchor)
    assert result.delta_seconds == 60.0


def test_pinpoint_delta_minutes_property(anchor):
    result = pinpoint("* * * * *", anchor)
    assert result.delta_minutes == pytest.approx(1.0)


def test_pinpoint_delta_hours_property(anchor):
    result = pinpoint("0 * * * *", anchor)
    assert result.delta_hours == pytest.approx(1.0)


def test_pinpoint_stores_expression(anchor):
    result = pinpoint("30 9 * * *", anchor)
    assert result.expression == "30 9 * * *"


def test_pinpoint_stores_anchor(anchor):
    result = pinpoint("* * * * *", anchor)
    assert result.anchor == anchor


def test_pinpoint_label_none_by_default(anchor):
    result = pinpoint("* * * * *", anchor)
    assert result.label is None


def test_pinpoint_label_propagated(anchor):
    result = pinpoint("* * * * *", anchor, label="heartbeat")
    assert result.label == "heartbeat"


def test_pinpoint_str_contains_expression(anchor):
    result = pinpoint("* * * * *", anchor)
    assert "* * * * *" in str(result)


def test_pinpoint_str_contains_label_when_set(anchor):
    result = pinpoint("* * * * *", anchor, label="myjob")
    assert "myjob" in str(result)


def test_pinpoint_str_no_bracket_when_no_label(anchor):
    result = pinpoint("* * * * *", anchor)
    assert "[" not in str(result)


def test_pinpoint_specific_time_next_day(anchor):
    # anchor is 12:00; next 09:30 is the following day
    result = pinpoint("30 9 * * *", anchor)
    assert result.target.hour == 9
    assert result.target.minute == 30
    assert result.target.day == 16


def test_pinpoint_many_returns_list(anchor):
    results = pinpoint_many(["* * * * *", "0 * * * *"], anchor)
    assert isinstance(results, list)
    assert len(results) == 2


def test_pinpoint_many_sorted_by_target(anchor):
    results = pinpoint_many(["0 * * * *", "* * * * *"], anchor)
    assert results[0].target <= results[1].target


def test_pinpoint_many_label_mismatch_raises(anchor):
    with pytest.raises(ValueError):
        pinpoint_many(["* * * * *", "0 * * * *"], anchor, labels=["only_one"])


def test_pinpoint_many_labels_propagated(anchor):
    results = pinpoint_many(["* * * * *"], anchor, labels=["tick"])
    assert results[0].label == "tick"


def test_pinpoint_many_empty_list_returns_empty(anchor):
    results = pinpoint_many([], anchor)
    assert results == []
