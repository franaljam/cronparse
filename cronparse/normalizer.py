"""Normalize cron expressions to a canonical form."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .parser import CronExpression, parse
from .alias import is_alias, resolve as resolve_alias


@dataclass
class NormalizedExpression:
    """A cron expression in canonical (fully-expanded) string form."""

    original: str
    canonical: str
    was_alias: bool
    expression: CronExpression

    def __str__(self) -> str:  # pragma: no cover
        return self.canonical


def _field_to_canonical(values: list[int], lo: int, hi: int) -> str:
    """Convert a sorted list of integers back to the most compact cron token."""
    full = list(range(lo, hi + 1))
    if values == full:
        return "*"

    # Detect uniform step starting from lo
    if len(values) >= 2:
        step = values[1] - values[0]
        if step > 1 and all(values[i] - values[i - 1] == step for i in range(1, len(values))):
            if values[0] == lo and values[-1] <= hi:
                return f"*/{step}"

    # Detect a contiguous range
    if len(values) > 1 and values == list(range(values[0], values[-1] + 1)):
        return f"{values[0]}-{values[-1]}"

    return ",".join(str(v) for v in values)


def normalize(expression: str) -> NormalizedExpression:
    """Return a *NormalizedExpression* for *expression*.

    Aliases such as ``@daily`` are first resolved to their raw cron string
    before parsing and canonicalization.
    """
    was_alias = is_alias(expression)
    raw = resolve_alias(expression) if was_alias else expression
    expr = parse(raw)

    bounds = [
        (expr.minute, 0, 59),
        (expr.hour, 0, 23),
        (expr.dom, 1, 31),
        (expr.month, 1, 12),
        (expr.dow, 0, 6),
    ]
    parts = [_field_to_canonical(field, lo, hi) for field, lo, hi in bounds]
    canonical = " ".join(parts)

    return NormalizedExpression(
        original=expression,
        canonical=canonical,
        was_alias=was_alias,
        expression=expr,
    )


def are_equivalent(a: str, b: str) -> bool:
    """Return *True* if *a* and *b* resolve to identical schedules."""
    return normalize(a).canonical == normalize(b).canonical
