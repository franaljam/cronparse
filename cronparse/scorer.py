"""Cron expression complexity scorer.

Assigns a numeric complexity score to a cron expression based on
how specific, varied, and intricate its fields are.
"""

from dataclasses import dataclass, field
from typing import Optional

from .parser import CronExpression, parse


@dataclass
class ScoreResult:
    """Result of scoring a cron expression."""

    expression: str
    label: Optional[str]
    score: int
    breakdown: dict

    def __str__(self) -> str:
        label_part = f" ({self.label})" if self.label else ""
        return f"{self.expression}{label_part} — complexity score: {self.score}"

    def summary(self) -> str:
        lines = [str(self)]
        for field_name, points in self.breakdown.items():
            lines.append(f"  {field_name}: +{points}")
        return "\n".join(lines)


def _score_field(values: list, field_min: int, field_max: int) -> int:
    """Score a single parsed field based on its value set."""
    total = field_max - field_min + 1
    count = len(values)

    if count == total:
        return 0  # wildcard — no complexity
    if count == 1:
        return 3  # single specific value
    if count <= total // 2:
        return 2  # partial range or list
    return 1  # most values covered


def score(expression: str, label: Optional[str] = None) -> ScoreResult:
    """Score the complexity of a cron expression.

    Args:
        expression: A valid cron expression string.
        label: Optional human-readable label.

    Returns:
        A ScoreResult with total score and per-field breakdown.
    """
    expr: CronExpression = parse(expression)

    field_ranges = [
        ("minute", expr.minute, 0, 59),
        ("hour", expr.hour, 0, 23),
        ("dom", expr.dom, 1, 31),
        ("month", expr.month, 1, 12),
        ("dow", expr.dow, 0, 6),
    ]

    breakdown = {}
    total = 0
    for name, values, mn, mx in field_ranges:
        pts = _score_field(values, mn, mx)
        breakdown[name] = pts
        total += pts

    return ScoreResult(
        expression=expression,
        label=label,
        score=total,
        breakdown=breakdown,
    )


def score_many(
    expressions: list,
    labels: Optional[list] = None,
) -> list:
    """Score multiple cron expressions.

    Args:
        expressions: List of cron expression strings.
        labels: Optional list of labels (same length as expressions).

    Returns:
        List of ScoreResult objects, sorted by score descending.
    """
    if labels is None:
        labels = [None] * len(expressions)
    if len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")

    results = [score(expr, lbl) for expr, lbl in zip(expressions, labels)]
    return sorted(results, key=lambda r: r.score, reverse=True)
