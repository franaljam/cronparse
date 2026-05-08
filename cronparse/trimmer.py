"""Trim cron expressions by removing redundant or overlapping values."""

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import CronExpression, parse


@dataclass
class TrimResult:
    expression: str
    original: str
    label: Optional[str]
    trimmed_fields: List[str]
    changes: List[str]

    def __str__(self) -> str:  # noqa: D105
        if self.changes:
            return f"{self.original} -> {self.expression} ({len(self.changes)} change(s))"
        return f"{self.expression} (no changes)"

    @property
    def was_modified(self) -> bool:
        return bool(self.changes)

    @property
    def change_count(self) -> int:
        return len(self.changes)


def _trim_field(values: List[int], lo: int, hi: int) -> tuple:
    """Return (trimmed_values, changes) for a field."""
    full = set(range(lo, hi + 1))
    value_set = set(values)
    changes = []

    # If values cover the full range, collapse to wildcard sentinel
    if value_set == full:
        changes.append(f"collapsed {len(values)} values to wildcard")
        return list(range(lo, hi + 1)), changes

    # Remove duplicates and sort
    deduped = sorted(set(values))
    if len(deduped) < len(values):
        changes.append(f"removed {len(values) - len(deduped)} duplicate(s)")

    return deduped, changes


def trim(expression: str, label: Optional[str] = None) -> TrimResult:
    """Trim a cron expression by removing redundant values."""
    expr: CronExpression = parse(expression)

    bounds = [
        (expr.minute, 0, 59),
        (expr.hour, 0, 23),
        (expr.dom, 1, 31),
        (expr.month, 1, 12),
        (expr.dow, 0, 6),
    ]
    field_names = ["minute", "hour", "dom", "month", "dow"]
    all_changes: List[str] = []
    trimmed_fields: List[str] = []
    parts: List[str] = []

    raw_parts = expression.split()

    for i, ((values, lo, hi), name) in enumerate(zip(bounds, field_names)):
        trimmed, changes = _trim_field(values, lo, hi)
        if changes:
            all_changes.extend(f"{name}: {c}" for c in changes)
            trimmed_fields.append(name)

        full = set(range(lo, hi + 1))
        if set(trimmed) == full:
            parts.append("*")
        elif raw_parts[i].startswith("*"):
            parts.append(raw_parts[i])
        else:
            parts.append(",".join(str(v) for v in trimmed))

    result_expr = " ".join(parts)
    return TrimResult(
        expression=result_expr,
        original=expression,
        label=label,
        trimmed_fields=trimmed_fields,
        changes=all_changes,
    )


def trim_many(
    expressions: List[str], labels: Optional[List[str]] = None
) -> List[TrimResult]:
    """Trim multiple cron expressions."""
    if labels is None:
        labels = [None] * len(expressions)
    if len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")
    return [trim(e, l) for e, l in zip(expressions, labels)]
