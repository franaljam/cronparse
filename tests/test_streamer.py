"""Tests for cronparse.streamer."""

from datetime import datetime, timezone

import pytest

from cronparse.streamer import StreamConfig, StreamResult, collect, stream


def dt(year=2024, month=1, day=1, hour=0, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)


def test_stream_returns_iterator():
    config = StreamConfig(expression="* * * * *", start=dt(), max_count=3)
    result = stream(config)
    items = list(result)
    assert len(items) == 3


def test_stream_result_type():
    config = StreamConfig(expression="* * * * *", start=dt(), max_count=1)
    items = collect(config)
    assert isinstance(items[0], StreamResult)


def test_stream_index_starts_at_one():
    config = StreamConfig(expression="* * * * *", start=dt(), max_count=3)
    items = collect(config)
    assert [r.index for r in items] == [1, 2, 3]


def test_stream_every_minute_increments():
    config = StreamConfig(expression="* * * * *", start=dt(), max_count=3)
    items = collect(config)
    minutes = [r.run_time.minute for r in items]
    assert minutes[1] == minutes[0] + 1


def test_stream_max_count_respected():
    config = StreamConfig(expression="* * * * *", start=dt(), max_count=10)
    items = collect(config)
    assert len(items) == 10


def test_stream_end_datetime_stops_stream():
    start = dt(hour=0, minute=0)
    end = dt(hour=0, minute=5)
    config = StreamConfig(expression="* * * * *", start=start, end=end)
    items = collect(config)
    assert all(r.run_time <= end for r in items)
    assert len(items) <= 6


def test_stream_label_propagated():
    config = StreamConfig(expression="* * * * *", start=dt(), max_count=2, label="myjob")
    items = collect(config)
    assert all(r.label == "myjob" for r in items)


def test_stream_label_none_by_default():
    config = StreamConfig(expression="* * * * *", start=dt(), max_count=1)
    items = collect(config)
    assert items[0].label is None


def test_stream_filter_fn_applied():
    # Only allow even minutes
    config = StreamConfig(
        expression="* * * * *",
        start=dt(),
        max_count=3,
        filter_fn=lambda d: d.minute % 2 == 0,
    )
    items = collect(config)
    assert all(r.run_time.minute % 2 == 0 for r in items)
    assert len(items) == 3


def test_stream_result_str_with_label():
    r = StreamResult(index=1, run_time=dt(), label="job")
    assert "[job]" in str(r)
    assert "#1" in str(r)


def test_stream_result_str_without_label():
    r = StreamResult(index=2, run_time=dt())
    assert "#2" in str(r)
    assert "[" not in str(r)


def test_collect_returns_list():
    config = StreamConfig(expression="0 * * * *", start=dt(), max_count=2)
    result = collect(config)
    assert isinstance(result, list)
