"""Summarize and compare multiple cron expressions as a report."""

from dataclasses import dataclass, field
from typing import List, Dict

from .parser import CronExpression, parse
from .humanizer import humanize
from .validator import validate


@dataclass
class ExpressionSummary:
    expression: str
    human: str
    valid: bool
    errors: List[str]
    field_counts: Dict[str, int]

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "human": self.human,
            "valid": self.valid,
            "errors": self.errors,
            "field_counts": self.field_counts,
        }


def _field_counts(expr: CronExpression) -> Dict[str, int]:
    names = ["minute", "hour", "day", "month", "weekday"]
    fields = [expr.minute, expr.hour, expr.day, expr.month, expr.weekday]
    return {name: len(f.values) for name, f in zip(names, fields)}


def summarize(expression: str) -> ExpressionSummary:
    """Return a summary for a single cron expression string."""
    result = validate(expression)
    valid = bool(result)
    errors = result.error_messages() if not valid else []

    try:
        expr = parse(expression)
        human = humanize(expr)
        counts = _field_counts(expr)
    except Exception as exc:  # noqa: BLE001
        human = ""
        counts = {}
        if not errors:
            errors = [str(exc)]

    return ExpressionSummary(
        expression=expression,
        human=human,
        valid=valid,
        errors=errors,
        field_counts=counts,
    )


def summarize_many(expressions: List[str]) -> List[ExpressionSummary]:
    """Return summaries for a list of cron expression strings."""
    return [summarize(expr) for expr in expressions]


def report(expressions: List[str]) -> str:
    """Render a plain-text report for multiple cron expressions."""
    summaries = summarize_many(expressions)
    lines = []
    for s in summaries:
        status = "OK" if s.valid else "INVALID"
        lines.append(f"[{status}] {s.expression}")
        if s.human:
            lines.append(f"  Human : {s.human}")
        if s.errors:
            for err in s.errors:
                lines.append(f"  Error : {err}")
        counts = ", ".join(f"{k}={v}" for k, v in s.field_counts.items())
        if counts:
            lines.append(f"  Fields: {counts}")
        lines.append("")
    return "\n".join(lines).rstrip()
