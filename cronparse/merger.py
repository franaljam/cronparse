"""Merge multiple cron expressions into a unified schedule description."""

from dataclasses import dataclass, field
from typing import List, Dict, Set

from .parser import CronExpression, parse
from .humanizer import humanize


@dataclass
class MergeResult:
    """Result of merging multiple cron expressions."""

    expressions: List[CronExpression]
    merged_fields: Dict[str, Set[int]]
    labels: List[str]

    def human_summary(self) -> str:
        """Return a human-readable summary of all merged expressions."""
        if not self.expressions:
            return "No expressions"
        lines = []
        for label, expr in zip(self.labels, self.expressions):
            lines.append(f"{label}: {humanize(expr)}")
        return "\n".join(lines)

    def common_minutes(self) -> Set[int]:
        """Return minute values shared by ALL expressions."""
        if not self.expressions:
            return set()
        sets = [set(e.minute) for e in self.expressions]
        result = sets[0]
        for s in sets[1:]:
            result = result & s
        return result

    def common_hours(self) -> Set[int]:
        """Return hour values shared by ALL expressions."""
        if not self.expressions:
            return set()
        sets = [set(e.hour) for e in self.expressions]
        result = sets[0]
        for s in sets[1:]:
            result = result & s
        return result

    def all_minutes(self) -> Set[int]:
        """Return union of all minute values across expressions."""
        result: Set[int] = set()
        for e in self.expressions:
            result |= set(e.minute)
        return result

    def all_hours(self) -> Set[int]:
        """Return union of all hour values across expressions."""
        result: Set[int] = set()
        for e in self.expressions:
            result |= set(e.hour)
        return result


def merge(expressions: List[str], labels: List[str] = None) -> MergeResult:
    """Parse and merge a list of cron expression strings.

    Args:
        expressions: List of cron expression strings.
        labels: Optional list of labels; defaults to 'expr_0', 'expr_1', ...

    Returns:
        MergeResult containing parsed expressions and merged field data.
    """
    if not expressions:
        return MergeResult(expressions=[], merged_fields={}, labels=[])

    if labels is None:
        labels = [f"expr_{i}" for i in range(len(expressions))]

    if len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")

    parsed = [parse(e) for e in expressions]

    merged_fields: Dict[str, Set[int]] = {
        "minute": set(),
        "hour": set(),
        "day": set(),
        "month": set(),
        "weekday": set(),
    }
    field_names = list(merged_fields.keys())
    for expr in parsed:
        for fname in field_names:
            merged_fields[fname] |= set(getattr(expr, fname))

    return MergeResult(expressions=parsed, merged_fields=merged_fields, labels=labels)
