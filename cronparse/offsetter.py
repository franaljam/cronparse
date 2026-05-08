"""Offset cron schedule runs by a fixed number of minutes."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from .parser import parse
from .scheduler import next_runs


@dataclass
class OffsetResult:
    """Result of offsetting a cron schedule."""

    expression: str
    offset_minutes: int
    original_runs: List[datetime]
    offset_runs: List[datetime]
    label: Optional[str] = None

    @property
    def count(self) -> int:
        return len(self.offset_runs)

    @property
    def first(self) -> Optional[datetime]:
        return self.offset_runs[0] if self.offset_runs else None

    @property
    def last(self) -> Optional[datetime]:
        return self.offset_runs[-1] if self.offset_runs else None

    def __str__(self) -> str:
        sign = "+" if self.offset_minutes >= 0 else ""
        label_part = f" [{self.label}]" if self.label else ""
        return (
            f"OffsetResult({self.expression}{label_part}, "
            f"offset={sign}{self.offset_minutes}m, runs={self.count})"
        )


def offset(
    expression: str,
    offset_minutes: int,
    start: datetime,
    n: int = 5,
    label: Optional[str] = None,
) -> OffsetResult:
    """Return the next *n* runs shifted by *offset_minutes*."""
    expr = parse(expression)
    originals = next_runs(expr, start=start, n=n)
    shifted = [dt + timedelta(minutes=offset_minutes) for dt in originals]
    return OffsetResult(
        expression=expression,
        offset_minutes=offset_minutes,
        original_runs=originals,
        offset_runs=shifted,
        label=label,
    )


def offset_many(
    expressions: List[str],
    offset_minutes: int,
    start: datetime,
    n: int = 5,
    labels: Optional[List[str]] = None,
) -> List[OffsetResult]:
    """Offset multiple expressions by the same number of minutes."""
    if labels is not None and len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")
    results = []
    for i, expr in enumerate(expressions):
        lbl = labels[i] if labels else None
        results.append(offset(expr, offset_minutes, start, n=n, label=lbl))
    return results
