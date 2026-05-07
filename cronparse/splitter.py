"""Split a cron expression into named field parts with metadata."""

from dataclasses import dataclass
from typing import List, Optional

from cronparse.parser import parse, CronExpression


FIELD_NAMES = ["minute", "hour", "dom", "month", "dow"]
FIELD_LABELS = {
    "minute": "Minute",
    "hour": "Hour",
    "dom": "Day of Month",
    "month": "Month",
    "dow": "Day of Week",
}


@dataclass
class SplitField:
    name: str
    label: str
    raw: str
    values: List[int]
    is_wildcard: bool

    def __str__(self) -> str:
        wildcard_marker = " (wildcard)" if self.is_wildcard else ""
        return f"{self.label}: {self.raw}{wildcard_marker}"


@dataclass
class SplitResult:
    expression: str
    label: Optional[str]
    fields: List[SplitField]

    def get(self, name: str) -> Optional[SplitField]:
        """Return the SplitField for a given field name, or None."""
        for field in self.fields:
            if field.name == name:
                return field
        return None

    def wildcard_fields(self) -> List[str]:
        """Return names of all wildcard fields."""
        return [f.name for f in self.fields if f.is_wildcard]

    def summary(self) -> str:
        lines = [f"Expression: {self.expression}"]
        if self.label:
            lines.append(f"Label: {self.label}")
        for field in self.fields:
            lines.append(f"  {field}")
        return "\n".join(lines)


def split(expression: str, label: Optional[str] = None) -> SplitResult:
    """Parse a cron expression and split it into structured SplitField parts."""
    expr: CronExpression = parse(expression)
    raw_parts = expression.split()

    field_objects = [
        expr.minute,
        expr.hour,
        expr.dom,
        expr.month,
        expr.dow,
    ]

    fields: List[SplitField] = []
    for i, name in enumerate(FIELD_NAMES):
        raw = raw_parts[i] if i < len(raw_parts) else "*"
        values = sorted(field_objects[i].values)
        is_wildcard = raw.strip() == "*"
        fields.append(SplitField(
            name=name,
            label=FIELD_LABELS[name],
            raw=raw,
            values=values,
            is_wildcard=is_wildcard,
        ))

    return SplitResult(expression=expression, label=label, fields=fields)
