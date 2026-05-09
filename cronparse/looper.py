"""Loop detection and cycle analysis for cron expressions."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from cronparse.parser import parse
from cronparse.scheduler import next_runs


@dataclass
class LoopCycle:
    """Represents a detected repeating cycle in a cron schedule."""

    period_minutes: int
    occurrences: int
    first: datetime
    last: datetime

    def __str__(self) -> str:
        return (
            f"LoopCycle(period={self.period_minutes}m, "
            f"occurrences={self.occurrences}, "
            f"first={self.first.isoformat()}, last={self.last.isoformat()})"
        )


@dataclass
class LoopResult:
    """Result of loop analysis on a cron expression."""

    expression: str
    label: Optional[str]
    cycle: Optional[LoopCycle]
    runs: List[datetime] = field(default_factory=list)

    @property
    def has_cycle(self) -> bool:
        return self.cycle is not None

    @property
    def summary(self) -> str:
        if self.cycle is None:
            return f"{self.expression}: no regular cycle detected"
        return (
            f"{self.expression}: repeats every {self.cycle.period_minutes} minute(s), "
            f"{self.cycle.occurrences} times in sample"
        )

    def __str__(self) -> str:
        return self.summary


def _detect_cycle(runs: List[datetime]) -> Optional[LoopCycle]:
    """Detect a consistent period among a list of run times."""
    if len(runs) < 2:
        return None

    gaps = [
        int((runs[i + 1] - runs[i]).total_seconds() // 60)
        for i in range(len(runs) - 1)
    ]

    if not gaps:
        return None

    base = gaps[0]
    if all(g == base for g in gaps):
        return LoopCycle(
            period_minutes=base,
            occurrences=len(runs),
            first=runs[0],
            last=runs[-1],
        )
    return None


def loop(
    expression: str,
    start: datetime,
    n: int = 10,
    label: Optional[str] = None,
) -> LoopResult:
    """Analyse a cron expression for repeating cycles.

    Args:
        expression: A cron expression string.
        start: The datetime from which to sample runs.
        n: Number of upcoming runs to sample.
        label: Optional label for the expression.

    Returns:
        A LoopResult describing the detected cycle (if any).
    """
    expr = parse(expression)
    runs = next_runs(expr, start, n)
    cycle = _detect_cycle(runs)
    return LoopResult(expression=expression, label=label, cycle=cycle, runs=runs)
