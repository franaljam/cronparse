"""Tests for cronparse.snapshot module."""

from datetime import datetime, timezone

import pytest

from cronparse.snapshot import (
    Snapshot,
    SnapshotDelta,
    take_snapshot,
    diff_snapshots,
)


FIXED_TS = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)


def test_take_snapshot_returns_snapshot():
    snap = take_snapshot("0 * * * *", captured_at=FIXED_TS)
    assert isinstance(snap, Snapshot)


def test_take_snapshot_stores_expression():
    snap = take_snapshot("0 * * * *", captured_at=FIXED_TS)
    assert snap.expression == "0 * * * *"


def test_take_snapshot_stores_label():
    snap = take_snapshot("0 * * * *", label="hourly", captured_at=FIXED_TS)
    assert snap.label == "hourly"


def test_take_snapshot_label_none_by_default():
    snap = take_snapshot("0 * * * *", captured_at=FIXED_TS)
    assert snap.label is None


def test_take_snapshot_stores_captured_at():
    snap = take_snapshot("0 * * * *", captured_at=FIXED_TS)
    assert snap.captured_at == FIXED_TS


def test_take_snapshot_human_readable_present():
    snap = take_snapshot("0 * * * *", captured_at=FIXED_TS)
    assert isinstance(snap.human_readable, str)
    assert len(snap.human_readable) > 0


def test_take_snapshot_fields_contain_all_keys():
    snap = take_snapshot("0 * * * *", captured_at=FIXED_TS)
    assert set(snap.fields.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_snapshot_str_contains_expression():
    snap = take_snapshot("0 * * * *", captured_at=FIXED_TS)
    assert "0 * * * *" in str(snap)


def test_snapshot_str_contains_label():
    snap = take_snapshot("0 * * * *", label="myjob", captured_at=FIXED_TS)
    assert "myjob" in str(snap)


def test_diff_identical_snapshots_no_changes():
    snap = take_snapshot("0 * * * *", captured_at=FIXED_TS)
    delta = diff_snapshots(snap, snap)
    assert not delta.has_changes


def test_diff_different_expressions_detects_changes():
    before = take_snapshot("0 * * * *", captured_at=FIXED_TS)
    after = take_snapshot("30 6 * * *", captured_at=FIXED_TS)
    delta = diff_snapshots(before, after)
    assert delta.has_changes


def test_diff_detects_minute_change():
    before = take_snapshot("0 * * * *", captured_at=FIXED_TS)
    after = take_snapshot("15 * * * *", captured_at=FIXED_TS)
    delta = diff_snapshots(before, after)
    assert "minute" in delta.changed_fields


def test_diff_no_spurious_fields():
    before = take_snapshot("0 6 * * *", captured_at=FIXED_TS)
    after = take_snapshot("0 9 * * *", captured_at=FIXED_TS)
    delta = diff_snapshots(before, after)
    assert "hour" in delta.changed_fields
    assert "minute" not in delta.changed_fields


def test_diff_summary_no_changes():
    snap = take_snapshot("* * * * *", captured_at=FIXED_TS)
    delta = diff_snapshots(snap, snap)
    assert "No changes" in delta.summary()


def test_diff_summary_with_changes():
    before = take_snapshot("0 * * * *", captured_at=FIXED_TS)
    after = take_snapshot("30 6 * * *", captured_at=FIXED_TS)
    delta = diff_snapshots(before, after)
    summary = delta.summary()
    assert "changed" in summary.lower()
