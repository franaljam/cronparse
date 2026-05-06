"""Segment a list of cron expressions into time-based buckets (hourly, daily, etc.)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from cronparse.parser import parse, CronExpression
from cronparse.comparator import frequency


SEGMENT_LABELS = ["minutely", "hourly", "daily", "weekly", "monthly", "rarely"]


@dataclass
class SegmentEntry:
    expression: str
    label: Optional[str]
    segment: str
    runs_per_day: float

    def __str__(self) -> str:
        tag = f" ({self.label})" if self.label else ""
        return f"{self.expression}{tag} -> {self.segment} (~{self.runs_per_day:.2f}/day)"


@dataclass
class SegmentResult:
    buckets: Dict[str, List[SegmentEntry]] = field(default_factory=dict)

    def all_entries(self) -> List[SegmentEntry]:
        return [e for entries in self.buckets.values() for e in entries]

    def summary(self) -> str:
        lines = []
        for seg in SEGMENT_LABELS:
            entries = self.buckets.get(seg, [])
            if entries:
                lines.append(f"{seg}: {len(entries)} expression(s)")
        return "\n".join(lines) if lines else "No expressions segmented."


def _runs_per_day(expr: CronExpression) -> float:
    """Estimate how many times per day an expression fires."""
    info = frequency(expr)
    return info.runs_per_day


def _classify_segment(runs: float) -> str:
    if runs >= 60 * 24:
        return "minutely"
    if runs >= 24:
        return "hourly"
    if runs >= 1:
        return "daily"
    if runs >= 1 / 7:
        return "weekly"
    if runs >= 1 / 31:
        return "monthly"
    return "rarely"


def segment(
    expressions: List[str],
    labels: Optional[List[str]] = None,
) -> SegmentResult:
    """Segment expressions into frequency-based buckets."""
    if labels is not None and len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")

    result = SegmentResult(buckets={seg: [] for seg in SEGMENT_LABELS})

    for i, raw in enumerate(expressions):
        label = labels[i] if labels else None
        expr = parse(raw)
        rpd = _runs_per_day(expr)
        seg = _classify_segment(rpd)
        entry = SegmentEntry(
            expression=raw,
            label=label,
            segment=seg,
            runs_per_day=rpd,
        )
        result.buckets[seg].append(entry)

    return result
