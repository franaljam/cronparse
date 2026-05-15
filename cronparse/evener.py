"""Even distribution analyzer — checks how evenly a cron expression distributes
firing times across a given period (hour or day)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

from cronparse.parser import parse
from cronparse.scheduler import iter_runs


@dataclass
class EvenResult:
    expression: str
    label: Optional[str]
    period_hours: int
    run_count: int
    expected_gap_minutes: float
    actual_gaps_minutes: List[float]
    min_gap_minutes: float
    max_gap_minutes: float
    variance: float
    is_even: bool

    def __str__(self) -> str:
        return (
            f"EvenResult({self.expression!r}, runs={self.run_count}, "
            f"gap_range=[{self.min_gap_minutes:.1f}, {self.max_gap_minutes:.1f}] min, "
            f"even={self.is_even})"
        )

    def summary(self) -> str:
        status = "evenly distributed" if self.is_even else "unevenly distributed"
        return (
            f"{self.expression!r} fires {self.run_count} time(s) over "
            f"{self.period_hours}h — {status} "
            f"(variance={self.variance:.2f})"
        )


_EVEN_VARIANCE_THRESHOLD = 1.0


def even(
    expression: str,
    *,
    period_hours: int = 24,
    anchor: Optional[datetime] = None,
    label: Optional[str] = None,
    threshold: float = _EVEN_VARIANCE_THRESHOLD,
) -> EvenResult:
    """Analyse how evenly *expression* distributes its runs over *period_hours*."""
    if anchor is None:
        anchor = datetime(2024, 1, 1, 0, 0, 0)

    end = anchor + timedelta(hours=period_hours)
    expr = parse(expression)
    runs: List[datetime] = []
    for run in iter_runs(expr, start=anchor):
        if run >= end:
            break
        runs.append(run)

    run_count = len(runs)
    gaps: List[float] = []
    for i in range(1, len(runs)):
        delta = (runs[i] - runs[i - 1]).total_seconds() / 60.0
        gaps.append(delta)

    if gaps:
        min_gap = min(gaps)
        max_gap = max(gaps)
        mean_gap = sum(gaps) / len(gaps)
        variance = sum((g - mean_gap) ** 2 for g in gaps) / len(gaps)
    else:
        min_gap = max_gap = mean_gap = variance = 0.0

    expected_gap = (period_hours * 60.0) / run_count if run_count > 1 else 0.0
    is_even = variance <= threshold

    return EvenResult(
        expression=expression,
        label=label,
        period_hours=period_hours,
        run_count=run_count,
        expected_gap_minutes=expected_gap,
        actual_gaps_minutes=gaps,
        min_gap_minutes=min_gap,
        max_gap_minutes=max_gap,
        variance=variance,
        is_even=is_even,
    )
