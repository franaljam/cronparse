"""Freezer: pause a cron schedule at a fixed point and resume after N runs."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .parser import parse
from .scheduler import next_runs


@dataclass
class FreezeResult:
    expression: str
    anchor: datetime
    skipped: int
    resume_at: Optional[datetime]
    runs_after_resume: List[datetime] = field(default_factory=list)
    label: Optional[str] = None

    @property
    def count(self) -> int:
        return len(self.runs_after_resume)

    @property
    def first(self) -> Optional[datetime]:
        return self.runs_after_resume[0] if self.runs_after_resume else None

    @property
    def last(self) -> Optional[datetime]:
        return self.runs_after_resume[-1] if self.runs_after_resume else None

    def __str__(self) -> str:
        tag = f" [{self.label}]" if self.label else ""
        return (
            f"FreezeResult{tag}: expr={self.expression!r}, "
            f"skipped={self.skipped}, resume_at={self.resume_at}, "
            f"runs_after={self.count}"
        )


def freeze(
    expression: str,
    anchor: datetime,
    skip: int = 1,
    n: int = 5,
    label: Optional[str] = None,
) -> FreezeResult:
    """Skip *skip* scheduled runs starting from *anchor*, then return *n* runs."""
    if skip < 0:
        raise ValueError("skip must be >= 0")
    if n < 0:
        raise ValueError("n must be >= 0")

    expr = parse(expression)

    # Collect skip + n runs so we can split them
    total_needed = skip + n
    if total_needed == 0:
        return FreezeResult(
            expression=expression,
            anchor=anchor,
            skipped=0,
            resume_at=None,
            runs_after_resume=[],
            label=label,
        )

    all_runs = next_runs(expr, start=anchor, n=total_needed)
    skipped_runs = all_runs[:skip]
    remaining = all_runs[skip:]

    resume_at = remaining[0] if remaining else (all_runs[-1] if all_runs else None)

    return FreezeResult(
        expression=expression,
        anchor=anchor,
        skipped=len(skipped_runs),
        resume_at=resume_at,
        runs_after_resume=remaining,
        label=label,
    )


def freeze_many(
    expressions: List[str],
    anchor: datetime,
    skip: int = 1,
    n: int = 5,
    labels: Optional[List[str]] = None,
) -> List[FreezeResult]:
    """Apply freeze to multiple expressions."""
    if labels is not None and len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")
    return [
        freeze(expr, anchor, skip=skip, n=n, label=(labels[i] if labels else None))
        for i, expr in enumerate(expressions)
    ]
