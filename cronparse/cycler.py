"""cycler.py — Detect and describe repeating cycles in cron schedules.

A 'cycle' here is the fixed interval (in minutes) between consecutive
firings of a cron expression over a rolling window.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from statistics import mean, stdev
from typing import List, Optional

from .parser import parse
from .scheduler import next_runs


@dataclass
class CycleResult:
    expression: str
    label: Optional[str]
    sample_size: int
    gaps: List[int]  # minutes between consecutive runs
    is_regular: bool
    interval_minutes: Optional[int]  # None if irregular
    mean_gap: float
    jitter: float  # stdev of gaps; 0.0 for perfectly regular

    def __str__(self) -> str:  # pragma: no cover
        regularity = "regular" if self.is_regular else "irregular"
        tag = f" ({self.label})" if self.label else ""
        interval = (
            f"{self.interval_minutes} min" if self.interval_minutes is not None
            else f"~{self.mean_gap:.1f} min avg"
        )
        return f"{self.expression}{tag}: {regularity}, interval={interval}"

    @property
    def count(self) -> int:
        return len(self.gaps)

    def summary(self) -> str:
        lines = [
            f"Expression : {self.expression}",
            f"Label      : {self.label or '—'}",
            f"Sample size: {self.sample_size} runs",
            f"Regular    : {self.is_regular}",
            f"Interval   : {self.interval_minutes if self.interval_minutes is not None else 'variable'} min",
            f"Mean gap   : {self.mean_gap:.2f} min",
            f"Jitter     : {self.jitter:.2f} min",
        ]
        return "\n".join(lines)


def _compute_gaps(runs: List[datetime]) -> List[int]:
    """Return list of integer minute-gaps between consecutive datetimes."""
    gaps: List[int] = []
    for a, b in zip(runs, runs[1:]):
        delta = int((b - a).total_seconds() // 60)
        gaps.append(delta)
    return gaps


def cycle(
    expression: str,
    *,
    anchor: Optional[datetime] = None,
    sample_size: int = 20,
    label: Optional[str] = None,
    jitter_threshold: float = 0.5,
) -> CycleResult:
    """Analyse the firing cycle of *expression*.

    Parameters
    ----------
    expression:
        A standard 5-field cron expression.
    anchor:
        Start datetime for sampling (UTC-aware).  Defaults to now.
    sample_size:
        How many future runs to collect before computing gaps.
    label:
        Optional human-readable label attached to the result.
    jitter_threshold:
        Maximum stdev (minutes) still considered a 'regular' schedule.
    """
    if anchor is None:
        anchor = datetime.now(timezone.utc)

    expr = parse(expression)
    runs = next_runs(expr, n=sample_size, start=anchor)

    if len(runs) < 2:
        return CycleResult(
            expression=expression,
            label=label,
            sample_size=sample_size,
            gaps=[],
            is_regular=False,
            interval_minutes=None,
            mean_gap=0.0,
            jitter=0.0,
        )

    gaps = _compute_gaps(runs)
    avg = mean(gaps)
    jitter = stdev(gaps) if len(gaps) > 1 else 0.0
    is_regular = jitter <= jitter_threshold
    interval = int(round(avg)) if is_regular else None

    return CycleResult(
        expression=expression,
        label=label,
        sample_size=sample_size,
        gaps=gaps,
        is_regular=is_regular,
        interval_minutes=interval,
        mean_gap=avg,
        jitter=jitter,
    )
