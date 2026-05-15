"""Fencer: restrict cron expression runs to allowed time boundaries."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Iterator, List, Optional

from cronparse.parser import parse
from cronparse.scheduler import iter_runs


@dataclass
class FenceResult:
    expression: str
    label: Optional[str]
    fence_start: time
    fence_end: time
    runs: List[datetime] = field(default_factory=list)

    def count(self) -> int:
        return len(self.runs)

    def first(self) -> Optional[datetime]:
        return self.runs[0] if self.runs else None

    def last(self) -> Optional[datetime]:
        return self.runs[-1] if self.runs else None

    def __str__(self) -> str:
        return (
            f"FenceResult(expr={self.expression!r}, "
            f"fence={self.fence_start}-{self.fence_end}, "
            f"count={self.count()})"
        )


def _within_fence(dt: datetime, fence_start: time, fence_end: time) -> bool:
    """Return True if dt's time falls within [fence_start, fence_end]."""
    t = dt.time().replace(second=0, microsecond=0)
    if fence_start <= fence_end:
        return fence_start <= t <= fence_end
    # Overnight fence (e.g. 22:00 – 06:00)
    return t >= fence_start or t <= fence_end


def fence(
    expression: str,
    anchor: datetime,
    fence_start: time,
    fence_end: time,
    n: int = 10,
    label: Optional[str] = None,
) -> FenceResult:
    """Return the next *n* runs of *expression* that fall within the fence window."""
    expr = parse(expression)
    runs: List[datetime] = []
    stream: Iterator[datetime] = iter_runs(expr, anchor)
    # Guard against infinite loops for impossible fences
    checked = 0
    max_check = n * 1500
    while len(runs) < n and checked < max_check:
        dt = next(stream)
        checked += 1
        if _within_fence(dt, fence_start, fence_end):
            runs.append(dt)
    return FenceResult(
        expression=expression,
        label=label,
        fence_start=fence_start,
        fence_end=fence_end,
        runs=runs,
    )


def fence_many(
    expressions: List[str],
    anchor: datetime,
    fence_start: time,
    fence_end: time,
    n: int = 10,
    labels: Optional[List[str]] = None,
) -> List[FenceResult]:
    """Apply fence() to multiple expressions."""
    if labels is not None and len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")
    return [
        fence(expr, anchor, fence_start, fence_end, n=n,
              label=labels[i] if labels else None)
        for i, expr in enumerate(expressions)
    ]
