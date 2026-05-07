"""Flatten a cron expression into an explicit list of (minute, hour) firing times within a day."""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .parser import CronExpression, parse


@dataclass
class FlattenResult:
    """Result of flattening a cron expression into discrete intra-day firing times."""

    expression: str
    label: Optional[str]
    times: List[Tuple[int, int]]  # (hour, minute) pairs, sorted

    @property
    def count(self) -> int:
        """Number of distinct firing times within a single day."""
        return len(self.times)

    def __str__(self) -> str:  # pragma: no cover
        label_part = f" ({self.label})" if self.label else ""
        return (
            f"FlattenResult[{self.expression}{label_part}]: "
            f"{self.count} firing(s)/day"
        )


def flatten(
    expression: str,
    *,
    label: Optional[str] = None,
) -> FlattenResult:
    """Return every (hour, minute) pair that fires within a single UTC day.

    Only the *minute* and *hour* fields are considered; day-of-month,
    month, and day-of-week fields are intentionally ignored so the
    result represents the intra-day firing pattern.
    """
    expr: CronExpression = parse(expression)

    times: List[Tuple[int, int]] = [
        (h, m)
        for h in sorted(expr.hour)
        for m in sorted(expr.minute)
    ]

    return FlattenResult(expression=expression, label=label, times=times)


def flatten_many(
    expressions: List[str],
    *,
    labels: Optional[List[str]] = None,
) -> List[FlattenResult]:
    """Flatten multiple expressions, optionally attaching labels."""
    if labels is not None and len(labels) != len(expressions):
        raise ValueError(
            f"labels length ({len(labels)}) must match "
            f"expressions length ({len(expressions)})"
        )

    return [
        flatten(
            expr,
            label=(labels[i] if labels else None),
        )
        for i, expr in enumerate(expressions)
    ]
