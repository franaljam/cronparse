"""Pinpointer: find the exact next firing time after a given datetime."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .parser import CronExpression, parse
from .scheduler import next_runs


@dataclass
class PinpointResult:
    """Result of a pinpoint lookup."""

    expression: str
    anchor: datetime
    target: datetime
    delta_seconds: float
    label: Optional[str] = None

    def __str__(self) -> str:
        label_part = f" [{self.label}]" if self.label else ""
        return (
            f"{self.expression}{label_part}: next firing at {self.target.isoformat()} "
            f"({self.delta_seconds:.0f}s from anchor)"
        )

    @property
    def delta_minutes(self) -> float:
        """Delta in minutes between anchor and target."""
        return self.delta_seconds / 60.0

    @property
    def delta_hours(self) -> float:
        """Delta in hours between anchor and target."""
        return self.delta_seconds / 3600.0


def pinpoint(
    expression: str,
    anchor: datetime,
    label: Optional[str] = None,
) -> PinpointResult:
    """Return the single next firing time for *expression* after *anchor*.

    Parameters
    ----------
    expression:
        A standard 5-field cron expression string.
    anchor:
        The reference datetime from which to search forward.
    label:
        Optional human-readable label for the expression.

    Returns
    -------
    PinpointResult
        Dataclass containing the target datetime and metadata.
    """
    expr: CronExpression = parse(expression)
    runs = next_runs(expr, anchor, n=1)
    target = runs[0]
    delta = (target - anchor).total_seconds()
    return PinpointResult(
        expression=expression,
        anchor=anchor,
        target=target,
        delta_seconds=delta,
        label=label,
    )


def pinpoint_many(
    expressions: list[str],
    anchor: datetime,
    labels: Optional[list[str]] = None,
) -> list[PinpointResult]:
    """Pinpoint the next firing time for each expression in *expressions*.

    Results are returned sorted by ascending target datetime.
    """
    if labels is not None and len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")
    resolved_labels = labels if labels is not None else [None] * len(expressions)
    results = [
        pinpoint(expr, anchor, label=lbl)
        for expr, lbl in zip(expressions, resolved_labels)
    ]
    return sorted(results, key=lambda r: r.target)
