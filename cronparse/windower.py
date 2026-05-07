"""Window-based run aggregator: collect cron runs within a time window."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from .parser import parse, CronExpression
from .scheduler import iter_runs


@dataclass
class WindowResult:
    expression: str
    start: datetime
    end: datetime
    runs: List[datetime] = field(default_factory=list)
    label: Optional[str] = None

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
        tag = f"{self.label}: " if self.label else ""
        return (
            f"{tag}{self.expression} — {self.count} run(s) "
            f"between {self.start.isoformat()} and {self.end.isoformat()}"
        )


def window(
    expression: str,
    start: datetime,
    hours: int = 24,
    label: Optional[str] = None,
) -> WindowResult:
    """Collect all runs of *expression* within [start, start + hours)."""
    if hours <= 0:
        raise ValueError("hours must be a positive integer")

    end = start + timedelta(hours=hours)
    expr: CronExpression = parse(expression)
    runs: List[datetime] = [
        dt
        for dt in iter_runs(expr, start, limit=hours * 60)
        if dt < end
    ]
    return WindowResult(
        expression=expression,
        start=start,
        end=end,
        runs=runs,
        label=label,
    )


def window_many(
    expressions: List[str],
    start: datetime,
    hours: int = 24,
    labels: Optional[List[str]] = None,
) -> List[WindowResult]:
    """Run *window* for multiple expressions."""
    if labels is not None and len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")
    return [
        window(
            expr,
            start,
            hours=hours,
            label=labels[i] if labels else None,
        )
        for i, expr in enumerate(expressions)
    ]
