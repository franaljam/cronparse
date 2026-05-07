"""Rewinder: compute past run times for a cron expression."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Iterator, List, Optional

from cronparse.parser import CronExpression, parse
from cronparse.scheduler import iter_runs


@dataclass
class RewindResult:
    """Container for past run times of a cron expression."""

    expression: str
    label: Optional[str]
    runs: List[datetime]

    @property
    def count(self) -> int:
        return len(self.runs)

    @property
    def earliest(self) -> Optional[datetime]:
        return self.runs[-1] if self.runs else None

    @property
    def latest(self) -> Optional[datetime]:
        return self.runs[0] if self.runs else None

    def __str__(self) -> str:
        label_part = f" ({self.label})" if self.label else ""
        return (
            f"RewindResult[{self.expression}{label_part}] "
            f"{self.count} past runs"
        )


def _iter_past(expr: CronExpression, before: datetime, n: int) -> Iterator[datetime]:
    """Yield up to *n* past fire times strictly before *before*."""
    # Walk backwards in 1-minute steps from (before - 1 min) for a wide window.
    # We collect forward runs in a rolling window to stay efficient.
    window_minutes = max(n * 60, 1440)  # at least one day
    start = before - timedelta(minutes=window_minutes)
    candidates = list(iter_runs(expr, start, n=window_minutes + 1))
    past = [dt for dt in candidates if dt < before]
    past.sort(reverse=True)
    for dt in past[:n]:
        yield dt


def rewind(
    expression: str,
    *,
    before: Optional[datetime] = None,
    n: int = 5,
    label: Optional[str] = None,
) -> RewindResult:
    """Return the *n* most recent past runs before *before* (default: now)."""
    if n < 1:
        raise ValueError("n must be >= 1")
    if before is None:
        before = datetime.utcnow().replace(second=0, microsecond=0)
    expr = parse(expression)
    runs = list(_iter_past(expr, before, n))
    return RewindResult(expression=expression, label=label, runs=runs)
