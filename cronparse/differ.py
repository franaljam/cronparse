"""Cron expression differ — compare two cron expressions and describe their differences."""

from dataclasses import dataclass
from typing import List, Optional

from .parser import CronExpression, parse
from .humanizer import humanize


FIELD_NAMES = ["minute", "hour", "day of month", "month", "day of week"]


@dataclass
class FieldDiff:
    field: str
    left: frozenset
    right: frozenset
    added: frozenset
    removed: frozenset

    def __str__(self) -> str:
        added = sorted(self.added)
        removed = sorted(self.removed)
        parts = []
        if added:
            parts.append(f"+{added}")
        if removed:
            parts.append(f"-{removed}")
        return f"{self.field}: {' '.join(parts)}"


@dataclass
class CronDiff:
    left_expr: str
    right_expr: str
    field_diffs: List[FieldDiff]
    left_human: str
    right_human: str

    @property
    def has_changes(self) -> bool:
        return bool(self.field_diffs)

    def summary(self) -> str:
        if not self.has_changes:
            return "Expressions are equivalent."
        lines = [
            f"Left:  {self.left_expr!r} → {self.left_human}",
            f"Right: {self.right_expr!r} → {self.right_human}",
            "Changes:",
        ]
        for diff in self.field_diffs:
            lines.append(f"  {diff}")
        return "\n".join(lines)


def diff(expr_a: str, expr_b: str) -> CronDiff:
    """Compare two cron expression strings and return a CronDiff."""
    cron_a = parse(expr_a)
    cron_b = parse(expr_b)
    return diff_expressions(cron_a, cron_b, expr_a, expr_b)


def diff_expressions(
    cron_a: CronExpression,
    cron_b: CronExpression,
    label_a: Optional[str] = None,
    label_b: Optional[str] = None,
) -> CronDiff:
    """Compare two parsed CronExpression objects and return a CronDiff."""
    fields_a = [cron_a.minute, cron_a.hour, cron_a.dom, cron_a.month, cron_a.dow]
    fields_b = [cron_b.minute, cron_b.hour, cron_b.dom, cron_b.month, cron_b.dow]

    diffs: List[FieldDiff] = []
    for name, fa, fb in zip(FIELD_NAMES, fields_a, fields_b):
        sa, sb = frozenset(fa), frozenset(fb)
        if sa != sb:
            diffs.append(FieldDiff(
                field=name,
                left=sa,
                right=sb,
                added=sb - sa,
                removed=sa - sb,
            ))

    return CronDiff(
        left_expr=label_a or "",
        right_expr=label_b or "",
        field_diffs=diffs,
        left_human=humanize(cron_a),
        right_human=humanize(cron_b),
    )
