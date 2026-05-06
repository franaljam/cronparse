"""Expression inspector: detailed field-by-field breakdown with value ranges."""

from dataclasses import dataclass, field
from typing import List, Optional
from cronparse.parser import CronExpression, parse


@dataclass
class FieldInspection:
    name: str
    raw: str
    values: List[int]
    min_value: Optional[int]
    max_value: Optional[int]
    is_wildcard: bool
    is_step: bool
    is_range: bool
    is_list: bool
    value_count: int

    def __str__(self) -> str:
        kind = "wildcard" if self.is_wildcard else (
            "step" if self.is_step else (
                "range" if self.is_range else (
                    "list" if self.is_list else "specific"
                )
            )
        )
        return (
            f"{self.name}: raw={self.raw!r} type={kind} "
            f"count={self.value_count} "
            f"range=[{self.min_value}, {self.max_value}]"
        )


@dataclass
class InspectionReport:
    expression: str
    fields: List[FieldInspection]

    def summary(self) -> str:
        lines = [f"Expression: {self.expression}"]
        for f in self.fields:
            lines.append(f"  {f}")
        return "\n".join(lines)

    def wildcard_fields(self) -> List[FieldInspection]:
        return [f for f in self.fields if f.is_wildcard]

    def restricted_fields(self) -> List[FieldInspection]:
        return [f for f in self.fields if not f.is_wildcard]


def _inspect_field(name: str, raw: str, values: List[int]) -> FieldInspection:
    is_wildcard = raw == "*" or raw.startswith("*/")
    is_step = "/" in raw
    is_range = "-" in raw and "/" not in raw
    is_list = "," in raw
    return FieldInspection(
        name=name,
        raw=raw,
        values=values,
        min_value=min(values) if values else None,
        max_value=max(values) if values else None,
        is_wildcard=is_wildcard,
        is_step=is_step,
        is_range=is_range,
        is_list=is_list,
        value_count=len(values),
    )


def inspect(expression: str) -> InspectionReport:
    """Parse and inspect a cron expression, returning a detailed report."""
    expr: CronExpression = parse(expression)
    field_names = ["minute", "hour", "dom", "month", "dow"]
    raw_parts = expression.split()
    fields = [
        _inspect_field(name, raw_parts[i], list(getattr(expr, name).values))
        for i, name in enumerate(field_names)
    ]
    return InspectionReport(expression=expression, fields=fields)
