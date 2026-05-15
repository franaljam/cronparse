"""Sampler: draw a random sample of firing times from a cron expression window."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .parser import parse
from .scheduler import iter_runs


@dataclass
class SampleResult:
    expression: str
    start: datetime
    end: datetime
    n: int
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
        tag = f" ({self.label})" if self.label else ""
        return (
            f"SampleResult{tag}: {self.count}/{self.n} samples "
            f"from {self.start.isoformat()} to {self.end.isoformat()}"
        )


def sample(
    expression: str,
    start: datetime,
    end: datetime,
    n: int = 10,
    seed: Optional[int] = None,
    label: Optional[str] = None,
) -> SampleResult:
    """Return up to *n* randomly sampled firing times within [start, end)."""
    if n < 0:
        raise ValueError("n must be non-negative")

    parse(expression)  # validate

    pool: List[datetime] = []
    for dt in iter_runs(expression, start):
        if dt >= end:
            break
        pool.append(dt)

    rng = random.Random(seed)
    chosen = sorted(rng.sample(pool, min(n, len(pool))))

    return SampleResult(
        expression=expression,
        start=start,
        end=end,
        n=n,
        runs=chosen,
        label=label,
    )


def sample_many(
    expressions: List[str],
    start: datetime,
    end: datetime,
    n: int = 10,
    seed: Optional[int] = None,
    labels: Optional[List[str]] = None,
) -> List[SampleResult]:
    """Sample multiple expressions, sharing the same window and sample size."""
    if labels is not None and len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")
    return [
        sample(
            expr,
            start,
            end,
            n=n,
            seed=seed,
            label=labels[i] if labels else None,
        )
        for i, expr in enumerate(expressions)
    ]
