"""Snapshot module: capture and compare cron expression states over time."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from cronparse.parser import CronExpression, parse
from cronparse.humanizer import humanize


@dataclass
class Snapshot:
    """A point-in-time capture of a cron expression."""

    expression: str
    label: Optional[str]
    captured_at: datetime
    human_readable: str
    fields: dict

    def __str__(self) -> str:
        label_part = f"[{self.label}] " if self.label else ""
        ts = self.captured_at.strftime("%Y-%m-%d %H:%M:%S UTC")
        return f"{label_part}{self.expression!r} captured at {ts}: {self.human_readable}"


@dataclass
class SnapshotDelta:
    """Difference between two snapshots of (potentially different) expressions."""

    before: Snapshot
    after: Snapshot
    changed_fields: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.changed_fields)

    def summary(self) -> str:
        if not self.has_changes:
            return "No changes between snapshots."
        fields_str = ", ".join(self.changed_fields)
        return (
            f"Expression changed from {self.before.expression!r} "
            f"to {self.after.expression!r}. "
            f"Fields changed: {fields_str}."
        )


def _expr_fields(expr: CronExpression) -> dict:
    return {
        "minute": sorted(expr.minute),
        "hour": sorted(expr.hour),
        "dom": sorted(expr.dom),
        "month": sorted(expr.month),
        "dow": sorted(expr.dow),
    }


def take_snapshot(
    expression: str,
    label: Optional[str] = None,
    captured_at: Optional[datetime] = None,
) -> Snapshot:
    """Parse a cron expression and capture its current state as a Snapshot."""
    expr: CronExpression = parse(expression)
    ts = captured_at or datetime.now(tz=timezone.utc)
    return Snapshot(
        expression=expression,
        label=label,
        captured_at=ts,
        human_readable=humanize(expr),
        fields=_expr_fields(expr),
    )


def diff_snapshots(before: Snapshot, after: Snapshot) -> SnapshotDelta:
    """Compute which fields changed between two snapshots."""
    changed: List[str] = [
        fname
        for fname in ("minute", "hour", "dom", "month", "dow")
        if before.fields.get(fname) != after.fields.get(fname)
    ]
    return SnapshotDelta(before=before, after=after, changed_fields=changed)
