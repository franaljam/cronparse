"""Match datetimes against cron expressions with detailed field-level results."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .parser import CronExpression, parse


@dataclass
class FieldMatchResult:
    """Result of matching a single cron field against a datetime component."""

    field_name: str
    value: int
    allowed: List[int]
    matched: bool

    def __str__(self) -> str:
        status = "✓" if self.matched else "✗"
        return f"{status} {self.field_name}: {self.value} in {self.allowed}"


@dataclass
class MatchResult:
    """Full match result for a cron expression against a datetime."""

    expression: str
    dt: datetime
    fields: List[FieldMatchResult] = field(default_factory=list)

    @property
    def matched(self) -> bool:
        return all(f.matched for f in self.fields)

    @property
    def failed_fields(self) -> List[FieldMatchResult]:
        return [f for f in self.fields if not f.matched]

    def summary(self) -> str:
        status = "MATCH" if self.matched else "NO MATCH"
        lines = [f"{status}: '{self.expression}' at {self.dt.isoformat()}"]
        for f in self.fields:
            lines.append(f"  {f}")
        return "\n".join(lines)


def _check_field(name: str, value: int, allowed: List[int]) -> FieldMatchResult:
    return FieldMatchResult(
        field_name=name,
        value=value,
        allowed=allowed,
        matched=value in allowed,
    )


def match(expression: str, dt: Optional[datetime] = None) -> MatchResult:
    """Match a cron expression against a datetime (defaults to now).

    Returns a MatchResult with per-field breakdown.
    """
    if dt is None:
        dt = datetime.now()

    expr: CronExpression = parse(expression)

    fields = [
        _check_field("minute", dt.minute, expr.minute),
        _check_field("hour", dt.hour, expr.hour),
        _check_field("day_of_month", dt.day, expr.day_of_month),
        _check_field("month", dt.month, expr.month),
        _check_field("day_of_week", dt.weekday(), [d % 7 for d in expr.day_of_week]),
    ]

    return MatchResult(expression=expression, dt=dt, fields=fields)


def matches(expression: str, dt: Optional[datetime] = None) -> bool:
    """Return True if the cron expression matches the given datetime."""
    return match(expression, dt).matched
