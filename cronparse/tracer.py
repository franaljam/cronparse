"""Execution tracer: records which fields matched for each scheduled run."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .parser import CronExpression, parse
from .scheduler import iter_runs
from .matcher import match


@dataclass
class TraceStep:
    """A single traced execution moment."""

    index: int
    dt: datetime
    matched_fields: dict  # field_name -> matched value
    label: Optional[str] = None

    def __str__(self) -> str:
        label_part = f"[{self.label}] " if self.label else ""
        fields = ", ".join(f"{k}={v}" for k, v in self.matched_fields.items())
        return f"{label_part}#{self.index} {self.dt.isoformat()} ({fields})"


@dataclass
class TraceResult:
    """Collection of traced steps for a cron expression."""

    expression: str
    steps: List[TraceStep] = field(default_factory=list)
    label: Optional[str] = None

    @property
    def count(self) -> int:
        return len(self.steps)

    def summary(self) -> str:
        lines = [f"Trace for '{self.expression}' ({self.count} steps):"]
        for step in self.steps:
            lines.append(f"  {step}")
        return "\n".join(lines)


def trace(
    expression: str,
    start: datetime,
    n: int = 5,
    label: Optional[str] = None,
) -> TraceResult:
    """Trace the next *n* runs of *expression* from *start*.

    Each step records which concrete value of each cron field was satisfied.
    """
    expr: CronExpression = parse(expression)
    result = TraceResult(expression=expression, label=label)

    for index, dt in enumerate(iter_runs(expr, start), start=1):
        if index > n:
            break
        mr = match(expression, dt)
        matched = {
            fr.field: fr.actual for fr in mr.field_results if fr.matched
        }
        step = TraceStep(index=index, dt=dt, matched_fields=matched, label=label)
        result.steps.append(step)

    return result
