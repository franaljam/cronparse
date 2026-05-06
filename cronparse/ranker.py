"""Rank cron expressions by frequency and specificity."""

from dataclasses import dataclass, field
from typing import List
from cronparse.parser import CronExpression, parse


@dataclass
class RankEntry:
    expression: str
    label: str
    runs_per_day: float
    specificity: int  # higher = more specific (fewer wildcards)
    rank: int = 0

    def __str__(self) -> str:
        return (
            f"[{self.rank}] {self.label or self.expression} "
            f"— {self.runs_per_day:.1f} runs/day, specificity={self.specificity}"
        )


def _runs_per_day(expr: CronExpression) -> float:
    """Estimate how many times an expression fires per day."""
    minutes = len(expr.minute)
    hours = len(expr.hour)
    return float(minutes * hours)


def _specificity(expr: CronExpression) -> int:
    """Count how many fields are NOT wildcards (more = more specific)."""
    total = 5
    wildcards = sum([
        len(expr.minute) == 60,
        len(expr.hour) == 24,
        len(expr.dom) == 31,
        len(expr.month) == 12,
        len(expr.dow) == 7,
    ])
    return total - wildcards


def rank(
    expressions: List[str],
    labels: List[str] = None,
    reverse: bool = False,
) -> List[RankEntry]:
    """Rank expressions from most to least frequent (or reversed)."""
    if labels and len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")

    entries = []
    for i, raw in enumerate(expressions):
        expr = parse(raw)
        label = labels[i] if labels else ""
        entries.append(RankEntry(
            expression=raw,
            label=label,
            runs_per_day=_runs_per_day(expr),
            specificity=_specificity(expr),
        ))

    entries.sort(key=lambda e: (e.runs_per_day, -e.specificity), reverse=not reverse)
    for i, entry in enumerate(entries, start=1):
        entry.rank = i

    return entries
