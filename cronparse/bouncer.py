"""Bouncer: check whether a cron expression will fire within a given time boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from .parser import parse
from .scheduler import iter_runs


@dataclass
class BounceResult:
    """Result of a boundary check for a cron expression."""

    expression: str
    start: datetime
    end: datetime
    fires: bool
    first_hit: Optional[datetime]
    label: Optional[str] = None

    def __str__(self) -> str:  # noqa: D401
        status = "fires" if self.fires else "does not fire"
        window = f"{self.start.isoformat()} -> {self.end.isoformat()}"
        tag = f"[{self.label}] " if self.label else ""
        return f"{tag}{self.expression} {status} in window {window}"

    @property
    def minutes_until_first(self) -> Optional[float]:
        """Minutes from *start* until the first firing, or None if no firing."""
        if self.first_hit is None:
            return None
        delta = self.first_hit - self.start
        return delta.total_seconds() / 60.0


def bounce(
    expression: str,
    start: datetime,
    end: datetime,
    *,
    label: Optional[str] = None,
) -> BounceResult:
    """Return a :class:`BounceResult` indicating whether *expression* fires between *start* and *end*.

    Parameters
    ----------
    expression:
        A standard five-field cron expression string.
    start:
        Inclusive lower bound of the window.
    end:
        Exclusive upper bound of the window.
    label:
        Optional human-readable label for the expression.
    """
    if end <= start:
        raise ValueError("end must be after start")

    parsed = parse(expression)
    first_hit: Optional[datetime] = None

    for run in iter_runs(parsed, start):
        if run >= end:
            break
        first_hit = run
        break

    return BounceResult(
        expression=expression,
        start=start,
        end=end,
        fires=first_hit is not None,
        first_hit=first_hit,
        label=label,
    )


def bounce_many(
    expressions: List[str],
    start: datetime,
    end: datetime,
    *,
    labels: Optional[List[str]] = None,
) -> List[BounceResult]:
    """Run :func:`bounce` for each expression in *expressions*."""
    if labels is not None and len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")
    return [
        bounce(
            expr,
            start,
            end,
            label=labels[i] if labels else None,
        )
        for i, expr in enumerate(expressions)
    ]
