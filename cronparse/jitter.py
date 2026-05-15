"""Jitter module: apply random offset to cron run times within a bounded range."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from .parser import parse
from .scheduler import next_runs


@dataclass
class JitterResult:
    expression: str
    offset_minutes: int
    label: Optional[str]
    runs: List[datetime]

    def count(self) -> int:
        return len(self.runs)

    def first(self) -> Optional[datetime]:
        return self.runs[0] if self.runs else None

    def last(self) -> Optional[datetime]:
        return self.runs[-1] if self.runs else None

    def __str__(self) -> str:
        tag = f" ({self.label})" if self.label else ""
        return (
            f"JitterResult{tag}: {self.count()} runs, "
            f"offset=±{self.offset_minutes}m, "
            f"first={self.first()}"
        )


def jitter(
    expression: str,
    anchor: datetime,
    n: int = 10,
    max_offset_minutes: int = 5,
    seed: Optional[int] = None,
    label: Optional[str] = None,
) -> JitterResult:
    """Return *n* upcoming runs from *anchor* with a random jitter applied.

    Each run is shifted by a random number of minutes in the range
    [-max_offset_minutes, +max_offset_minutes].
    """
    if max_offset_minutes < 0:
        raise ValueError("max_offset_minutes must be >= 0")

    rng = random.Random(seed)
    expr = parse(expression)
    base_runs = next_runs(expr, anchor, n)

    jittered: List[datetime] = []
    for run in base_runs:
        offset = rng.randint(-max_offset_minutes, max_offset_minutes)
        jittered.append(run + timedelta(minutes=offset))

    return JitterResult(
        expression=expression,
        offset_minutes=max_offset_minutes,
        label=label,
        runs=jittered,
    )


def jitter_many(
    expressions: List[str],
    anchor: datetime,
    n: int = 10,
    max_offset_minutes: int = 5,
    seed: Optional[int] = None,
    labels: Optional[List[str]] = None,
) -> List[JitterResult]:
    """Apply jitter to multiple expressions."""
    if labels is not None and len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")

    results = []
    for i, expr in enumerate(expressions):
        lbl = labels[i] if labels else None
        child_seed = None if seed is None else seed + i
        results.append(
            jitter(expr, anchor, n=n, max_offset_minutes=max_offset_minutes,
                   seed=child_seed, label=lbl)
        )
    return results
