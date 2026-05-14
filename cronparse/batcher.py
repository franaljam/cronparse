"""Batch execution planner: groups cron runs into fixed-size time batches."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from .parser import parse
from .scheduler import next_runs


@dataclass
class BatchWindow:
    """A single time batch containing zero or more scheduled runs."""

    index: int
    start: datetime
    end: datetime
    runs: List[datetime] = field(default_factory=list)

    def __str__(self) -> str:  # pragma: no cover
        return (
            f"Batch {self.index}: {self.start.isoformat()} – {self.end.isoformat()} "
            f"({len(self.runs)} run(s))"
        )

    @property
    def count(self) -> int:
        return len(self.runs)

    @property
    def is_empty(self) -> bool:
        return len(self.runs) == 0


@dataclass
class BatchResult:
    """Result of batching a cron expression over a time range."""

    expression: str
    label: Optional[str]
    batch_minutes: int
    windows: List[BatchWindow] = field(default_factory=list)

    def __str__(self) -> str:  # pragma: no cover
        non_empty = sum(1 for w in self.windows if not w.is_empty)
        return (
            f"BatchResult({self.expression!r}, {len(self.windows)} windows, "
            f"{non_empty} non-empty)"
        )

    @property
    def count(self) -> int:
        return len(self.windows)

    @property
    def non_empty_windows(self) -> List[BatchWindow]:
        return [w for w in self.windows if not w.is_empty]

    @property
    def total_runs(self) -> int:
        return sum(w.count for w in self.windows)

    def summary(self) -> str:
        return (
            f"{self.expression}: {self.total_runs} run(s) across "
            f"{len(self.non_empty_windows)}/{self.count} windows "
            f"({self.batch_minutes}-min batches)"
        )


def batch(
    expression: str,
    start: datetime,
    num_windows: int,
    batch_minutes: int = 60,
    label: Optional[str] = None,
) -> BatchResult:
    """Group scheduled runs into fixed-size time windows.

    Args:
        expression: Cron expression string.
        start: Window start (inclusive).
        num_windows: How many batch windows to create.
        batch_minutes: Duration of each window in minutes.
        label: Optional label for the result.

    Returns:
        BatchResult with populated windows.
    """
    expr = parse(expression)
    end = start + timedelta(minutes=batch_minutes * num_windows)

    # Collect all runs in the full range
    total_slots = batch_minutes * num_windows
    all_runs = next_runs(expr, start, n=total_slots)
    all_runs = [r for r in all_runs if r < end]

    windows: List[BatchWindow] = []
    for i in range(num_windows):
        w_start = start + timedelta(minutes=batch_minutes * i)
        w_end = w_start + timedelta(minutes=batch_minutes)
        window_runs = [r for r in all_runs if w_start <= r < w_end]
        windows.append(BatchWindow(index=i + 1, start=w_start, end=w_end, runs=window_runs))

    return BatchResult(
        expression=expression,
        label=label,
        batch_minutes=batch_minutes,
        windows=windows,
    )
