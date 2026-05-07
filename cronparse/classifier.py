"""Classify cron expressions into broad schedule categories."""

from dataclasses import dataclass
from typing import Optional

from cronparse.parser import CronExpression, parse


# Category constants
CATEGORY_MINUTELY = "minutely"
CATEGORY_HOURLY = "hourly"
CATEGORY_DAILY = "daily"
CATEGORY_WEEKLY = "weekly"
CATEGORY_MONTHLY = "monthly"
CATEGORY_CUSTOM = "custom"


@dataclass
class ClassificationResult:
    """Result of classifying a cron expression."""

    expression: str
    category: str
    label: Optional[str]
    confidence: float  # 0.0 – 1.0

    def __str__(self) -> str:
        label_part = f" ({self.label})" if self.label else ""
        return (
            f"{self.expression}{label_part} → {self.category} "
            f"[confidence={self.confidence:.2f}]"
        )


def _all_wildcard(values: list[int], full: list[int]) -> bool:
    return set(values) == set(full)


def classify(
    expression: str,
    label: Optional[str] = None,
) -> ClassificationResult:
    """Classify a cron expression into a human schedule category."""
    expr: CronExpression = parse(expression)

    minutes_full = list(range(60))
    hours_full = list(range(24))
    dom_full = list(range(1, 32))
    dow_full = list(range(7))

    all_minutes = _all_wildcard(expr.minute, minutes_full)
    all_hours = _all_wildcard(expr.hour, hours_full)
    all_dom = _all_wildcard(expr.day_of_month, dom_full)
    all_dow = _all_wildcard(expr.day_of_week, dow_full)

    if all_minutes and all_hours and all_dom and all_dow:
        return ClassificationResult(expression, CATEGORY_MINUTELY, label, 1.0)

    if all_minutes and all_dom and all_dow and not all_hours:
        return ClassificationResult(expression, CATEGORY_HOURLY, label, 1.0)

    if not all_hours and not all_minutes and all_dom and all_dow:
        return ClassificationResult(expression, CATEGORY_DAILY, label, 0.9)

    if not all_dow and all_dom:
        return ClassificationResult(expression, CATEGORY_WEEKLY, label, 0.85)

    if not all_dom and all_dow:
        return ClassificationResult(expression, CATEGORY_MONTHLY, label, 0.85)

    return ClassificationResult(expression, CATEGORY_CUSTOM, label, 0.6)


def classify_many(
    expressions: list[str],
    labels: Optional[list[str]] = None,
) -> list[ClassificationResult]:
    """Classify multiple cron expressions."""
    if labels is not None and len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")
    resolved_labels = labels if labels is not None else [None] * len(expressions)
    return [
        classify(expr, lbl)
        for expr, lbl in zip(expressions, resolved_labels)
    ]
