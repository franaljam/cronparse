"""Predict whether a cron expression will fire within a given time window."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from .parser import parse, CronExpression
from .scheduler import iter_runs


@dataclass
class PredictionResult:
    expression: str
    window_start: datetime
    window_end: datetime
    fires: bool
    occurrences: List[datetime] = field(default_factory=list)
    label: Optional[str] = None

    def count(self) -> int:
        return len(self.occurrences)

    def first(self) -> Optional[datetime]:
        return self.occurrences[0] if self.occurrences else None

    def last(self) -> Optional[datetime]:
        return self.occurrences[-1] if self.occurrences else None

    def __str__(self) -> str:
        tag = f"[{self.label}] " if self.label else ""
        if not self.fires:
            return f"{tag}`{self.expression}` does not fire in window"
        return (
            f"{tag}`{self.expression}` fires {self.count()} time(s) "
            f"between {self.window_start.isoformat()} and {self.window_end.isoformat()}"
        )


def predict(
    expression: str,
    window_start: datetime,
    window_end: datetime,
    label: Optional[str] = None,
) -> PredictionResult:
    """Return all occurrences of *expression* within [window_start, window_end]."""
    if window_end <= window_start:
        raise ValueError("window_end must be after window_start")

    expr: CronExpression = parse(expression)
    occurrences: List[datetime] = []

    for run in iter_runs(expr, window_start - timedelta(minutes=1)):
        if run > window_end:
            break
        if window_start <= run <= window_end:
            occurrences.append(run)

    return PredictionResult(
        expression=expression,
        window_start=window_start,
        window_end=window_end,
        fires=bool(occurrences),
        occurrences=occurrences,
        label=label,
    )


def predict_many(
    expressions: List[str],
    window_start: datetime,
    window_end: datetime,
    labels: Optional[List[str]] = None,
) -> List[PredictionResult]:
    """Run predict() for multiple expressions over the same window."""
    if labels is not None and len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")
    resolved_labels = labels if labels is not None else [None] * len(expressions)
    return [
        predict(expr, window_start, window_end, label=lbl)
        for expr, lbl in zip(expressions, resolved_labels)
    ]
