"""Syntax highlighter for cron expressions — annotates each field with ANSI colors."""

from dataclasses import dataclass
from typing import List

from cronparse.parser import CronExpression, parse

# ANSI color codes
_RESET = "\033[0m"
_COLORS = [
    "\033[36m",  # cyan   — minute
    "\033[32m",  # green  — hour
    "\033[33m",  # yellow — day-of-month
    "\033[35m",  # magenta — month
    "\033[34m",  # blue   — day-of-week
]
_FIELD_NAMES = ["minute", "hour", "dom", "month", "dow"]


@dataclass
class HighlightedField:
    name: str
    raw: str
    color_code: str

    def colored(self) -> str:
        """Return the raw token wrapped in its ANSI color."""
        return f"{self.color_code}{self.raw}{_RESET}"

    def __str__(self) -> str:  # pragma: no cover
        return self.colored()


@dataclass
class HighlightedExpression:
    expression: CronExpression
    fields: List[HighlightedField]

    def render(self) -> str:
        """Return the full expression with each field colored."""
        return " ".join(f.colored() for f in self.fields)

    def legend(self) -> str:
        """Return a legend line mapping colors to field names."""
        parts = [
            f"{f.color_code}{f.name}{_RESET}"
            for f in self.fields
        ]
        return "  ".join(parts)

    def __str__(self) -> str:  # pragma: no cover
        return self.render()


def highlight(expression: str) -> HighlightedExpression:
    """Parse *expression* and return a :class:`HighlightedExpression`.

    Args:
        expression: A standard five-field cron expression string.

    Returns:
        A :class:`HighlightedExpression` whose fields carry color metadata.
    """
    expr = parse(expression)
    raw_tokens = expression.split()
    if len(raw_tokens) != 5:
        raise ValueError(f"Expected 5 fields, got {len(raw_tokens)}: {expression!r}")

    fields = [
        HighlightedField(name=_FIELD_NAMES[i], raw=raw_tokens[i], color_code=_COLORS[i])
        for i in range(5)
    ]
    return HighlightedExpression(expression=expr, fields=fields)
