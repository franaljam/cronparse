"""capper.py — Limit cron runs to at most N occurrences within a time window."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from cronparse.parser import parse
from cronparse.scheduler import iter_runs


@dataclass
class CapResult:
    expression: str
    cap: int
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
        """True if the result was limited by the cap (not by the window)."""
        return self.count == self.cap

    def __str__(self) -> str:
        label_part = f" [{self.label}]" if self.label else ""
        return (
            f"CapResult{label_part}: {self.expression!r} "
            f"cap={self.cap} hits={self.count} capped={self.capped}"
        )


def cap(
    expression: str,
    start: datetime,
    end: datetime,
    max_runs: int,
    label: Optional[str] = None,
) -> CapResult:
    """Return at most *max_runs* firing times for *expression* in [start, end)."""
    if max_runs < 0:
        raise ValueError("max_runs must be >= 0")

    expr = parse(expression)
    collected: List[datetime] = []

    for dt in iter_runs(expr, start):
        if dt >= end:
            break
        collected.append(dt)
        if len(collected) >= max_runs:
            break

    return CapResult(
        expression=expression,
        cap=max_runs,
        runs=collected,
        label=label,
    )


def cap_many(
    expressions: List[str],
    start: datetime,
    end: datetime,
    max_runs: int,
    labels: Optional[List[str]] = None,
) -> List[CapResult]:
    """Apply :func:`cap` to multiple expressions."""
    if labels is not None and len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")
    return [
        cap(
            expr,
            start,
            end,
            max_runs,
            label=labels[i] if labels else None,
        )
        for i, expr in enumerate(expressions)
    ]
