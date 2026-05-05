"""Tests for cronparse.history module."""

from datetime import datetime, timezone

import pytest

from cronparse.history import (
    RunRecord,
    RunHistory,
    build_history,
    filter_history,
)


START = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


def test_build_history_returns_run_history():
    h = build_history("* * * * *", START, 5)
    assert isinstance(h, RunHistory)


def test_build_history_correct_count():
    h = build_history("* * * * *", START, 10)
    assert h.count == 10


def test_build_history_records_are_run_records():
    h = build_history("0 * * * *", START, 3)
    for r in h.records:
        assert isinstance(r, RunRecord)


def test_build_history_label_propagated():
    h = build_history("0 9 * * *", START, 2, label="morning")
    for r in h.records:
        assert r.label == "morning"


def test_build_history_no_label_is_none():
    h = build_history("0 9 * * *", START, 1)
    assert h.records[0].label is None


def test_history_earliest_and_latest():
    h = build_history("* * * * *", START, 5)
    assert h.earliest.scheduled_at <= h.latest.scheduled_at


def test_history_empty_latest_is_none():
    h = RunHistory(expression="* * * * *")
    assert h.latest is None
    assert h.earliest is None


def test_run_record_str_with_label():
    dt = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    r = RunRecord(expression="0 12 * * *", scheduled_at=dt, label="noon")
    assert "noon" in str(r)
    assert "0 12 * * *" in str(r)


def test_run_record_str_without_label():
    dt = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    r = RunRecord(expression="0 12 * * *", scheduled_at=dt)
    assert "[" not in str(r)


def test_history_summary_contains_expression():
    h = build_history("0 6 * * *", START, 3)
    summary = h.summary()
    assert "0 6 * * *" in summary
    assert "Runs" in summary


def test_history_summary_empty():
    h = RunHistory(expression="0 6 * * *")
    assert "No history" in h.summary()


def test_filter_history_after():
    h = build_history("* * * * *", START, 10)
    cutoff = h.records[4].scheduled_at
    filtered = filter_history(h, after=cutoff)
    assert all(r.scheduled_at >= cutoff for r in filtered.records)


def test_filter_history_before():
    h = build_history("* * * * *", START, 10)
    cutoff = h.records[5].scheduled_at
    filtered = filter_history(h, before=cutoff)
    assert all(r.scheduled_at <= cutoff for r in filtered.records)


def test_filter_history_preserves_expression():
    h = build_history("*/5 * * * *", START, 5)
    filtered = filter_history(h)
    assert filtered.expression == h.expression


def test_filter_history_window_reduces_count():
    h = build_history("* * * * *", START, 20)
    after = h.records[5].scheduled_at
    before = h.records[10].scheduled_at
    filtered = filter_history(h, after=after, before=before)
    assert filtered.count <= 20
    assert filtered.count > 0
