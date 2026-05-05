"""Annotator module: attach human-readable notes and metadata to cron fields."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from cronparse.parser import CronExpression, parse
from cronparse.humanizer import humanize


@dataclass
class FieldAnnotation:
    """Annotation for a single cron field."""
    field_name: str
    raw: str
    values: List[int]
    note: str

    def __str__(self) -> str:
        return f"{self.field_name}: {self.raw!r} -> {self.note}"


@dataclass
class AnnotatedExpression:
    """A parsed cron expression with per-field annotations."""
    expression: str
    human: str
    annotations: Dict[str, FieldAnnotation] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [f"Expression : {self.expression}", f"Human      : {self.human}"]
        for ann in self.annotations.values():
            lines.append(f"  {ann}")
        return "\n".join(lines)


_FIELD_NAMES = ["minute", "hour", "day", "month", "weekday"]

_NOTES: Dict[str, Dict[str, str]] = {
    "minute": {
        "wildcard": "runs every minute",
        "single": "at a fixed minute",
        "range": "within a minute range",
        "step": "every N minutes",
        "list": "at specific minutes",
    },
    "hour": {
        "wildcard": "every hour",
        "single": "at a fixed hour",
        "range": "within an hour range",
        "step": "every N hours",
        "list": "at specific hours",
    },
    "day": {
        "wildcard": "every day of month",
        "single": "on a specific day",
        "range": "over a range of days",
        "step": "every N days",
        "list": "on specific days",
    },
    "month": {
        "wildcard": "every month",
        "single": "in a specific month",
        "range": "over a range of months",
        "step": "every N months",
        "list": "in specific months",
    },
    "weekday": {
        "wildcard": "any day of week",
        "single": "on a specific weekday",
        "range": "over a weekday range",
        "step": "every N weekdays",
        "list": "on specific weekdays",
    },
}


def _classify(raw: str) -> str:
    if raw == "*":
        return "wildcard"
    if "/" in raw:
        return "step"
    if "-" in raw:
        return "range"
    if "," in raw:
        return "list"
    return "single"


def annotate(expression: str) -> AnnotatedExpression:
    """Parse *expression* and return an AnnotatedExpression with field notes."""
    expr: CronExpression = parse(expression)
    human = humanize(expr)
    parts = expression.split()
    annotations: Dict[str, FieldAnnotation] = {}
    field_values = [
        expr.minute, expr.hour, expr.day, expr.month, expr.weekday
    ]
    for idx, name in enumerate(_FIELD_NAMES):
        raw = parts[idx]
        kind = _classify(raw)
        note = _NOTES[name].get(kind, kind)
        annotations[name] = FieldAnnotation(
            field_name=name,
            raw=raw,
            values=list(field_values[idx]),
            note=note,
        )
    return AnnotatedExpression(expression=expression, human=human, annotations=annotations)
