"""curtailer.py — Limit cron runs to a maximum count within a time window."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .parser import parse
from .scheduler import iter_runs


@dataclass
class CurtailResult:
    expression: str
    limit: int
    window_hours: int
    runs: List[datetime]
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

    @property
    def capped(self) -> bool:
        """True if the limit was reached before the window was exhausted."""
        return self.count == self.limit

    def __str__(self) -> str:
        label_part = f" [{self.label}]" if self.label else ""
        return (
            f"CurtailResult{label_part}: {self.count}/{self.limit} runs "
            f"over {self.window_hours}h window (capped={self.capped})"
        )


def curtail(
    expression: str,
    start: datetime,
    *,
    limit: int = 10,
    window_hours: int = 24,
    label: Optional[str] = None,
) -> CurtailResult:
    """Collect up to *limit* scheduled runs within *window_hours* from *start*."""
    if limit < 1:
        raise ValueError("limit must be >= 1")
    if window_hours < 1:
        raise ValueError("window_hours must be >= 1")

    expr = parse(expression)
    from datetime import timedelta

    end = start + timedelta(hours=window_hours)
    collected: List[datetime] = []

    for dt in iter_runs(expr, start):
        if dt >= end or len(collected) >= limit:
            break
        collected.append(dt)

    return CurtailResult(
        expression=expression,
        limit=limit,
        window_hours=window_hours,
        runs=collected,
        label=label,
    )


def curtail_many(
    expressions: List[str],
    start: datetime,
    *,
    limit: int = 10,
    window_hours: int = 24,
    labels: Optional[List[str]] = None,
) -> List[CurtailResult]:
    """Apply :func:`curtail` to multiple expressions."""
    if labels is not None and len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")
    return [
        curtail(
            expr,
            start,
            limit=limit,
            window_hours=window_hours,
            label=labels[i] if labels else None,
        )
        for i, expr in enumerate(expressions)
    ]
