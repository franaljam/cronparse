"""Estimate the number of times a cron expression fires within a given time window."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from cronparse.parser import parse
from cronparse.scheduler import iter_runs


@dataclass
class EstimateResult:
    """Result of a firing estimate over a time window."""

    expression: str
    label: Optional[str]
    window_start: datetime
    window_end: datetime
    estimated_count: int
    runs_per_day: float

    def __str__(self) -> str:
        label_part = f" ({self.label})" if self.label else ""
        return (
            f"{self.expression}{label_part}: ~{self.estimated_count} fires "
            f"between {self.window_start.isoformat()} and {self.window_end.isoformat()} "
            f"({self.runs_per_day:.2f}/day)"
        )

    def summary(self) -> str:
        return (
            f"Estimated {self.estimated_count} runs over "
            f"{(self.window_end - self.window_start).days} day(s)"
        )


def estimate(
    expression: str,
    window_start: datetime,
    window_end: datetime,
    label: Optional[str] = None,
) -> EstimateResult:
    """Count how many times *expression* fires in [window_start, window_end).

    Uses a fast sampling approach: collect actual runs within the window.
    """
    if window_end <= window_start:
        raise ValueError("window_end must be after window_start")

    expr = parse(expression)
    delta_days = (window_end - window_start).total_seconds() / 86400.0

    # Collect all runs within the window
    count = 0
    for run in iter_runs(expr, window_start):
        if run >= window_end:
            break
        count += 1

    runs_per_day = count / delta_days if delta_days > 0 else 0.0

    return EstimateResult(
        expression=expression,
        label=label,
        window_start=window_start,
        window_end=window_end,
        estimated_count=count,
        runs_per_day=runs_per_day,
    )


def estimate_many(
    expressions: list[str],
    window_start: datetime,
    window_end: datetime,
    labels: Optional[list[str]] = None,
) -> list[EstimateResult]:
    """Estimate firing counts for multiple expressions."""
    if labels is not None and len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")
    resolved_labels: list[Optional[str]] = labels if labels is not None else [None] * len(expressions)
    return [
        estimate(expr, window_start, window_end, lbl)
        for expr, lbl in zip(expressions, resolved_labels)
    ]
