"""Core cron expression parser module."""

from dataclasses import dataclass
from typing import List, Optional


CRON_FIELDS = ["minute", "hour", "day_of_month", "month", "day_of_week"]

MONTH_NAMES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

DAY_NAMES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3,
    "thu": 4, "fri": 5, "sat": 6,
}

FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 6),
}


@dataclass
class CronField:
    name: str
    raw: str
    values: List[int]


@dataclass
class CronExpression:
    raw: str
    minute: CronField
    hour: CronField
    day_of_month: CronField
    month: CronField
    day_of_week: CronField


def _resolve_names(token: str, field: str) -> str:
    token = token.lower()
    if field == "month":
        for name, num in MONTH_NAMES.items():
            token = token.replace(name, str(num))
    elif field == "day_of_week":
        for name, num in DAY_NAMES.items():
            token = token.replace(name, str(num))
    return token


def _parse_field(raw: str, field: str) -> CronField:
    min_val, max_val = FIELD_RANGES[field]
    raw_resolved = _resolve_names(raw, field)
    values: List[int] = []

    for part in raw_resolved.split(","):
        if part == "*":
            values.extend(range(min_val, max_val + 1))
        elif "/" in part:
            base, step = part.split("/", 1)
            step = int(step)
            start = min_val if base == "*" else int(base.split("-")[0])
            end = max_val if base == "*" else (int(base.split("-")[1]) if "-" in base else max_val)
            values.extend(range(start, end + 1, step))
        elif "-" in part:
            start, end = part.split("-", 1)
            values.extend(range(int(start), int(end) + 1))
        else:
            values.append(int(part))

    values = sorted(set(v for v in values if min_val <= v <= max_val))
    return CronField(name=field, raw=raw, values=values)


def parse(expression: str) -> CronExpression:
    """Parse a cron expression string into a CronExpression object."""
    parts = expression.strip().split()
    if len(parts) != 5:
        raise ValueError(
            f"Invalid cron expression '{expression}': expected 5 fields, got {len(parts)}"
        )
    fields = {name: _parse_field(raw, name) for name, raw in zip(CRON_FIELDS, parts)}
    return CronExpression(
        raw=expression,
        minute=fields["minute"],
        hour=fields["hour"],
        day_of_month=fields["day_of_month"],
        month=fields["month"],
        day_of_week=fields["day_of_week"],
    )
