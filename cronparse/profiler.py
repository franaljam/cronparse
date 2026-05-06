"""Expression profiler: compute runtime characteristics of a cron expression."""

from dataclasses import dataclass, field
from typing import List, Optional

from cronparse.parser import CronExpression, parse
from cronparse.scheduler import next_runs

import datetime


@dataclass
class ProfileResult:
    expression: str
    label: Optional[str]
    runs_per_day: float
    runs_per_hour: float
    avg_gap_seconds: float
    min_gap_seconds: float
    max_gap_seconds: float
    sample_size: int

    def __str__(self) -> str:
        parts = []
        if self.label:
            parts.append(f"Label     : {self.label}")
        parts.append(f"Expression: {self.expression}")
        parts.append(f"Runs/day  : {self.runs_per_day:.2f}")
        parts.append(f"Runs/hour : {self.runs_per_hour:.4f}")
        parts.append(f"Avg gap   : {self.avg_gap_seconds:.1f}s")
        parts.append(f"Min gap   : {self.min_gap_seconds:.1f}s")
        parts.append(f"Max gap   : {self.max_gap_seconds:.1f}s")
        parts.append(f"Sample    : {self.sample_size} runs")
        return "\n".join(parts)


def _compute_gaps(runs: List[datetime.datetime]) -> List[float]:
    """Return list of gap durations in seconds between consecutive runs."""
    if len(runs) < 2:
        return []
    return [
        (runs[i + 1] - runs[i]).total_seconds()
        for i in range(len(runs) - 1)
    ]


def profile(
    expression: str,
    *,
    label: Optional[str] = None,
    sample: int = 200,
    start: Optional[datetime.datetime] = None,
) -> ProfileResult:
    """Profile a cron expression by sampling *sample* future run times.

    Args:
        expression: A valid cron expression string.
        label: Optional human-readable label.
        sample: Number of future runs to sample (min 2, max 10000).
        start: Reference datetime (defaults to UTC now).

    Returns:
        A :class:`ProfileResult` with timing statistics.
    """
    sample = max(2, min(sample, 10_000))
    if start is None:
        start = datetime.datetime.utcnow().replace(second=0, microsecond=0)

    expr: CronExpression = parse(expression)
    runs = next_runs(expr, n=sample, start=start)

    gaps = _compute_gaps(runs)

    if gaps:
        avg_gap = sum(gaps) / len(gaps)
        min_gap = min(gaps)
        max_gap = max(gaps)
    else:
        avg_gap = min_gap = max_gap = 0.0

    # Estimate daily / hourly rates from average gap
    runs_per_day = (86400.0 / avg_gap) if avg_gap > 0 else 0.0
    runs_per_hour = (3600.0 / avg_gap) if avg_gap > 0 else 0.0

    return ProfileResult(
        expression=expression,
        label=label,
        runs_per_day=runs_per_day,
        runs_per_hour=runs_per_hour,
        avg_gap_seconds=avg_gap,
        min_gap_seconds=min_gap,
        max_gap_seconds=max_gap,
        sample_size=len(runs),
    )
