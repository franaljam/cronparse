"""Cron expression linter: detects suspicious or non-portable patterns."""

from dataclasses import dataclass, field
from typing import List

from cronparse.parser import CronExpression, parse


@dataclass
class LintWarning:
    field_name: str
    code: str
    message: str

    def __str__(self) -> str:
        return f"[{self.code}] {self.field_name}: {self.message}"


@dataclass
class LintResult:
    expression: str
    warnings: List[LintWarning] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.warnings) == 0

    def summary(self) -> str:
        if self.clean:
            return f"{self.expression!r} — no issues found"
        lines = [f"{self.expression!r} — {len(self.warnings)} warning(s):"]
        lines.extend(f"  {w}" for w in self.warnings)
        return "\n".join(lines)


_FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]
_FIELD_MAX = {"minute": 59, "hour": 23, "day_of_month": 31, "month": 12, "day_of_week": 7}


def _check_dom_dow_both_set(expr: CronExpression) -> List[LintWarning]:
    """Warn when both day-of-month and day-of-week are non-wildcard (non-portable)."""
    warnings = []
    dom = expr.day_of_month
    dow = expr.day_of_week
    if set(dom) != set(range(1, 32)) and set(dow) != set(range(0, 8)):
        warnings.append(LintWarning(
            "day_of_month/day_of_week",
            "W001",
            "Both day-of-month and day-of-week are restricted; "
            "behaviour varies across cron implementations.",
        ))
    return warnings


def _check_step_one(expr: CronExpression) -> List[LintWarning]:
    """Warn on */1 patterns — equivalent to wildcard but noisy."""
    warnings = []
    pairs = [
        ("minute", expr.minute, 60),
        ("hour", expr.hour, 24),
        ("day_of_month", expr.day_of_month, 31),
        ("month", expr.month, 12),
        ("day_of_week", expr.day_of_week, 7),
    ]
    for name, values, total in pairs:
        if len(values) == total:
            continue  # already wildcard-like, skip
        if len(values) > 1:
            diffs = [values[i + 1] - values[i] for i in range(len(values) - 1)]
            if len(set(diffs)) == 1 and diffs[0] == 1:
                warnings.append(LintWarning(
                    name,
                    "W002",
                    "Step of 1 detected; consider using '*' instead.",
                ))
    return warnings


def _check_day_of_week_seven(expr: CronExpression) -> List[LintWarning]:
    """Warn if day-of-week contains 7 (Sunday) alongside 0 — redundant."""
    warnings = []
    dow = set(expr.day_of_week)
    if 0 in dow and 7 in dow:
        warnings.append(LintWarning(
            "day_of_week",
            "W003",
            "Both 0 and 7 represent Sunday; specifying both is redundant.",
        ))
    return warnings


def lint(expression: str) -> LintResult:
    """Lint a cron expression string and return a LintResult."""
    expr = parse(expression)
    result = LintResult(expression=expression)
    result.warnings.extend(_check_dom_dow_both_set(expr))
    result.warnings.extend(_check_step_one(expr))
    result.warnings.extend(_check_day_of_week_seven(expr))
    return result
