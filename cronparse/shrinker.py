"""Shrinker: reduce a cron expression to its minimal equivalent field representation."""

from dataclasses import dataclass, field
from typing import Optional
from cronparse.parser import CronExpression, parse


@dataclass
class ShrinkResult:
    expression: str
    original: str
    label: Optional[str]
    fields: dict  # field_name -> shrunk token
    changed_fields: list  # names of fields that were changed

    def __str__(self) -> str:
        label_part = f"{self.label}: " if self.label else ""
        return f"{label_part}{self.expression}"

    @property
    def was_modified(self) -> bool:
        return len(self.changed_fields) > 0

    @property
    def summary(self) -> str:
        if not self.was_modified:
            return f"No changes: {self.expression}"
        fields = ", ".join(self.changed_fields)
        return f"Shrunk fields [{fields}]: {self.original} -> {self.expression}"


def _shrink_token(token: str, lo: int, hi: int) -> str:
    """Attempt to simplify a token within its valid range."""
    if token == "*":
        return "*"
    # Expand list and see if it covers the full range
    try:
        values = sorted(int(v) for v in token.split(",") if "/" not in v and "-" not in v)
        if len(values) == (hi - lo + 1) and values[0] == lo and values[-1] == hi:
            return "*"
    except ValueError:
        pass
    # Range that covers full span -> wildcard
    if "-" in token and "/" not in token:
        parts = token.split("-")
        if len(parts) == 2:
            try:
                a, b = int(parts[0]), int(parts[1])
                if a == lo and b == hi:
                    return "*"
            except ValueError:
                pass
    # Step of 1 -> wildcard
    if token.startswith("*/1"):
        return "*"
    if "/" in token:
        base, step = token.split("/", 1)
        if step == "1":
            return base if base != "*" else "*"
    return token


def shrink(expression: str, label: Optional[str] = None) -> ShrinkResult:
    """Shrink a cron expression to its minimal representation."""
    expr: CronExpression = parse(expression)
    ranges = {
        "minute": (0, 59),
        "hour": (0, 23),
        "dom": (1, 31),
        "month": (1, 12),
        "dow": (0, 6),
    }
    raw_fields = {
        "minute": expr.minute_token,
        "hour": expr.hour_token,
        "dom": expr.dom_token,
        "month": expr.month_token,
        "dow": expr.dow_token,
    }
    shrunk = {}
    changed = []
    for name, token in raw_fields.items():
        lo, hi = ranges[name]
        new_token = _shrink_token(token, lo, hi)
        shrunk[name] = new_token
        if new_token != token:
            changed.append(name)
    new_expr = " ".join([
        shrunk["minute"], shrunk["hour"], shrunk["dom"],
        shrunk["month"], shrunk["dow"]
    ])
    return ShrinkResult(
        expression=new_expr,
        original=expression,
        label=label,
        fields=shrunk,
        changed_fields=changed,
    )
