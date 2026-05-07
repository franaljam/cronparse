"""Pause/resume simulation for cron expressions.

Given a cron expression and a reference datetime, a PauseResult
describes how long until the next firing is 'paused' (i.e. skipped)
and what the subsequent resumed firing would be.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from .parser import parse
from .scheduler import next_runs


@dataclass
class PauseResult:
    expression: str
    label: Optional[str]
    anchor: datetime
    skipped: List[datetime]
    resumed_at: Optional[datetime]

    def count(self) -> int:
        """Number of skipped runs."""
        return len(self.skipped)

    def __str__(self) -> str:
        label_part = f" ({self.label})" if self.label else ""
        if not self.skipped:
            return f"{self.expression}{label_part}: no runs to skip"
        skipped_str = ", ".join(dt.isoformat() for dt in self.skipped)
        resumed_str = self.resumed_at.isoformat() if self.resumed_at else "none"
        return (
            f"{self.expression}{label_part}: skipped {self.count()} run(s) "
            f"[{skipped_str}], resumes at {resumed_str}"
        )


def pause(
    expression: str,
    anchor: datetime,
    skip: int = 1,
    label: Optional[str] = None,
) -> PauseResult:
    """Simulate pausing a cron schedule by skipping `skip` upcoming runs.

    Args:
        expression: A valid cron expression string.
        anchor:     The reference datetime from which to look forward.
        skip:       How many upcoming runs to skip (default 1).
        label:      Optional human-readable label.

    Returns:
        A PauseResult containing the skipped runs and the next resumed run.
    """
    if skip < 0:
        raise ValueError("skip must be >= 0")

    expr = parse(expression)
    # Fetch skip+1 runs so we can identify the resumed run after the skipped ones
    runs = next_runs(expr, n=skip + 1, after=anchor)

    skipped = runs[:skip]
    resumed = runs[skip] if len(runs) > skip else None

    return PauseResult(
        expression=expression,
        label=label,
        anchor=anchor,
        skipped=skipped,
        resumed_at=resumed,
    )


def pause_many(
    expressions: List[str],
    anchor: datetime,
    skip: int = 1,
    labels: Optional[List[str]] = None,
) -> List[PauseResult]:
    """Apply pause() to multiple expressions."""
    if labels is not None and len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")
    return [
        pause(
            expr,
            anchor,
            skip=skip,
            label=labels[i] if labels else None,
        )
        for i, expr in enumerate(expressions)
    ]
