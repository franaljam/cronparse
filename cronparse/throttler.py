"""Throttler: limit cron runs to at most N per time window."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from cronparse.parser import parse
from cronparse.scheduler import iter_runs


@dataclass
class ThrottleResult:
    """Result of throttling a cron expression to N runs per window."""

    expression: str
    max_per_window: int
    window_minutes: int
    runs: List[datetime]
    label: Optional[str] = None
    dropped: int = 0

    @property
    def count(self) -> int:
        return len(self.runs)

    @property
    def first(self) -> Optional[datetime]:
        return self.runs[0] if self.runs else None

    @property
    def last(self) -> Optional[datetime]:
        return self.runs[-1] if self.runs else None

    def __str__(self) -> str:
        parts = [f"ThrottleResult({self.expression!r}"]
        if self.label:
            parts.append(f", label={self.label!r}")
        parts.append(
            f", kept={self.count}, dropped={self.dropped}"
            f", max={self.max_per_window}/window"
        )
        parts.append(")")
        return "".join(parts)


def throttle(
    expression: str,
    start: datetime,
    total_runs: int = 20,
    max_per_window: int = 3,
    window_minutes: int = 60,
    label: Optional[str] = None,
) -> ThrottleResult:
    """Collect up to *total_runs* scheduled datetimes, keeping at most
    *max_per_window* per rolling window of *window_minutes* minutes.

    Args:
        expression: A cron expression string.
        start: The reference datetime to begin scheduling from.
        total_runs: Maximum number of candidate runs to inspect.
        max_per_window: Maximum runs allowed within each window.
        window_minutes: Size of each rolling window in minutes.
        label: Optional label for the result.

    Returns:
        ThrottleResult with the kept and dropped counts.
    """
    expr = parse(expression)
    window_delta = timedelta(minutes=window_minutes)
    kept: List[datetime] = []
    dropped = 0
    window_runs: List[datetime] = []

    for run in iter_runs(expr, start):
        if len(kept) + dropped >= total_runs:
            break
        # Evict runs outside the current window
        window_runs = [r for r in window_runs if run - r < window_delta]
        if len(window_runs) < max_per_window:
            kept.append(run)
            window_runs.append(run)
        else:
            dropped += 1

    return ThrottleResult(
        expression=expression,
        max_per_window=max_per_window,
        window_minutes=window_minutes,
        runs=kept,
        label=label,
        dropped=dropped,
    )
