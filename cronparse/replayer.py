"""Replayer: re-run a cron expression over a past time window and collect results."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Iterator, List, Optional

from .parser import CronExpression, parse
from .scheduler import iter_runs


@dataclass
class ReplayResult:
    """Holds the results of replaying a cron expression over a past window."""

    expression: CronExpression
    start: datetime
    end: datetime
    runs: List[datetime] = field(default_factory=list)
    label: Optional[str] = None

    @property
    def count(self) -> int:
        return len(self.runs)

    @property
    def earliest(self) -> Optional[datetime]:
        return self.runs[0] if self.runs else None

    @property
    def latest(self) -> Optional[datetime]:
        return self.runs[-1] if self.runs else None

    def __str__(self) -> str:
        tag = f"{self.label}: " if self.label else ""
        return (
            f"{tag}{self.count} run(s) between "
            f"{self.start.isoformat()} and {self.end.isoformat()}"
        )


def _iter_past(expr: CronExpression, start: datetime, end: datetime) -> Iterator[datetime]:
    """Yield all scheduled times in [start, end) by scanning minute-by-minute backward."""
    current = start.replace(second=0, microsecond=0)
    while current <= end:
        minute = current.minute
        hour = current.hour
        dom = current.day
        month = current.month
        dow = current.weekday()  # 0=Monday; cron uses 0=Sunday, adjust
        dow_cron = (current.isoweekday() % 7)  # 0=Sunday

        if (
            minute in expr.minute
            and hour in expr.hour
            and dom in expr.dom
            and month in expr.month
            and dow_cron in expr.dow
        ):
            yield current
        current += timedelta(minutes=1)


def replay(
    expression: str,
    start: datetime,
    end: datetime,
    label: Optional[str] = None,
) -> ReplayResult:
    """Replay a cron expression over [start, end] and return matching run times."""
    expr = parse(expression)
    runs = list(_iter_past(expr, start, end))
    return ReplayResult(expression=expr, start=start, end=end, runs=runs, label=label)


def replay_many(
    expressions: List[str],
    start: datetime,
    end: datetime,
    labels: Optional[List[str]] = None,
) -> List[ReplayResult]:
    """Replay multiple expressions over the same window."""
    if labels is not None and len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")
    return [
        replay(expr, start, end, label=(labels[i] if labels else None))
        for i, expr in enumerate(expressions)
    ]
