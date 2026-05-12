"""Aligner: align multiple cron expressions to a common reference time."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .parser import parse
from .scheduler import next_runs


@dataclass
class AlignedEntry:
    expression: str
    label: Optional[str]
    aligned_at: datetime
    offset_minutes: float

    def __str__(self) -> str:
        lbl = f"[{self.label}] " if self.label else ""
        return (
            f"{lbl}{self.expression} -> "
            f"{self.aligned_at.strftime('%Y-%m-%d %H:%M')} "
            f"(+{self.offset_minutes:.1f} min)"
        )


@dataclass
class AlignResult:
    reference: datetime
    entries: List[AlignedEntry] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.entries)

    @property
    def earliest(self) -> Optional[AlignedEntry]:
        if not self.entries:
            return None
        return min(self.entries, key=lambda e: e.aligned_at)

    @property
    def latest(self) -> Optional[AlignedEntry]:
        if not self.entries:
            return None
        return max(self.entries, key=lambda e: e.aligned_at)

    def summary(self) -> str:
        if not self.entries:
            return "No expressions aligned."
        return (
            f"{self.count} expression(s) aligned from "
            f"{self.reference.strftime('%Y-%m-%d %H:%M')}; "
            f"spread: {self.latest.offset_minutes - self.earliest.offset_minutes:.1f} min"
        )


def align(
    expressions: List[str],
    reference: datetime,
    labels: Optional[List[str]] = None,
) -> AlignResult:
    """Find the next run of each expression at or after *reference*."""
    if labels is not None and len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")

    result = AlignResult(reference=reference)
    for idx, expr_str in enumerate(expressions):
        label = labels[idx] if labels else None
        expr = parse(expr_str)
        runs = next_runs(expr, reference, n=1)
        if not runs:
            continue
        aligned_at = runs[0]
        delta = (aligned_at - reference).total_seconds() / 60.0
        result.entries.append(
            AlignedEntry(
                expression=expr_str,
                label=label,
                aligned_at=aligned_at,
                offset_minutes=round(delta, 4),
            )
        )
    return result
