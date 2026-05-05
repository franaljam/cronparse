"""Cron expression validator with detailed error reporting."""

from dataclasses import dataclass, field
from typing import List, Optional

FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day": (1, 31),
    "month": (1, 12),
    "weekday": (0, 7),
}

FIELD_NAMES = list(FIELD_RANGES.keys())


@dataclass
class ValidationError:
    field: str
    message: str

    def __str__(self) -> str:
        return f"[{self.field}] {self.message}"


@dataclass
class ValidationResult:
    valid: bool
    errors: List[ValidationError] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.valid

    def error_messages(self) -> List[str]:
        return [str(e) for e in self.errors]


def _validate_value(value: int, lo: int, hi: int) -> bool:
    return lo <= value <= hi


def _validate_part(part: str, field_name: str, lo: int, hi: int) -> Optional[str]:
    """Validate a single part of a cron field. Returns error message or None."""
    if part == "*":
        return None

    if "/" in part:
        base, step = part.split("/", 1)
        if not step.isdigit() or int(step) < 1:
            return f"Invalid step value '{step}'; must be a positive integer"
        if base != "*":
            err = _validate_part(base, field_name, lo, hi)
            if err:
                return err
        return None

    if "-" in part:
        bounds = part.split("-", 1)
        if len(bounds) != 2 or not bounds[0].isdigit() or not bounds[1].isdigit():
            return f"Invalid range '{part}'"
        start, end = int(bounds[0]), int(bounds[1])
        if not _validate_value(start, lo, hi) or not _validate_value(end, lo, hi):
            return f"Range '{part}' out of bounds [{lo}-{hi}]"
        if start > end:
            return f"Range start {start} is greater than end {end}"
        return None

    if part.isdigit():
        val = int(part)
        if not _validate_value(val, lo, hi):
            return f"Value {val} out of bounds [{lo}-{hi}]"
        return None

    return f"Unrecognized token '{part}'"


def validate(expression: str) -> ValidationResult:
    """Validate a cron expression string. Returns a ValidationResult."""
    errors: List[ValidationError] = []
    parts = expression.strip().split()

    if len(parts) != 5:
        errors.append(ValidationError(
            "expression",
            f"Expected 5 fields, got {len(parts)}"
        ))
        return ValidationResult(valid=False, errors=errors)

    for part, fname in zip(parts, FIELD_NAMES):
        lo, hi = FIELD_RANGES[fname]
        for segment in part.split(","):
            msg = _validate_part(segment, fname, lo, hi)
            if msg:
                errors.append(ValidationError(field=fname, message=msg))

    return ValidationResult(valid=len(errors) == 0, errors=errors)
