"""Clone and mutate cron expressions by substituting individual fields."""

from dataclasses import dataclass, field
from typing import Optional

from .parser import CronExpression, parse


@dataclass
class CloneResult:
    """Result of cloning a cron expression with field substitutions."""

    original: str
    cloned: str
    substitutions: dict  # field_name -> new_value
    label: Optional[str] = None

    def __str__(self) -> str:
        parts = [f"original={self.original!r}", f"cloned={self.cloned!r}"]
        if self.label:
            parts.append(f"label={self.label!r}")
        return f"CloneResult({', '.join(parts)})"

    @property
    def changed_fields(self) -> list:
        return list(self.substitutions.keys())

    @property
    def was_modified(self) -> bool:
        return bool(self.substitutions)


_FIELD_ORDER = ["minute", "hour", "dom", "month", "dow"]


def clone(
    expression: str,
    *,
    minute: Optional[str] = None,
    hour: Optional[str] = None,
    dom: Optional[str] = None,
    month: Optional[str] = None,
    dow: Optional[str] = None,
    label: Optional[str] = None,
) -> CloneResult:
    """Clone a cron expression, optionally replacing one or more fields.

    Args:
        expression: A valid cron expression string.
        minute: Replacement for the minute field, or None to keep original.
        hour: Replacement for the hour field, or None to keep original.
        dom: Replacement for the day-of-month field, or None to keep original.
        month: Replacement for the month field, or None to keep original.
        dow: Replacement for the day-of-week field, or None to keep original.
        label: Optional label for the result.

    Returns:
        CloneResult with the new expression and a record of substitutions.
    """
    expr = parse(expression)
    overrides = {
        "minute": minute,
        "hour": hour,
        "dom": dom,
        "month": month,
        "dow": dow,
    }

    original_fields = [
        expr.minute,
        expr.hour,
        expr.dom,
        expr.month,
        expr.dow,
    ]

    new_parts = []
    substitutions = {}
    for i, fname in enumerate(_FIELD_ORDER):
        override = overrides[fname]
        if override is not None:
            new_parts.append(override)
            if override != original_fields[i]:
                substitutions[fname] = override
        else:
            new_parts.append(original_fields[i])

    cloned_str = " ".join(new_parts)
    # Validate the cloned expression by parsing it
    parse(cloned_str)

    return CloneResult(
        original=expression,
        cloned=cloned_str,
        substitutions=substitutions,
        label=label,
    )
