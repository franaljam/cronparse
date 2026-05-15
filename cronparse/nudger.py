"""Nudger: shift cron expression firing times by a fixed minute offset."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import CronExpression, parse


@dataclass
class NudgeResult:
    expression: str
    offset_minutes: int
    original_expression: str
    label: Optional[str] = None
    nudged_tokens: List[str] = field(default_factory=list)

    def __str__(self) -> str:  # noqa: D105
        return (
            f"NudgeResult(original={self.original_expression!r}, "
            f"nudged={self.expression!r}, offset={self.offset_minutes:+d}min)"
        )

    @property
    def was_modified(self) -> bool:
        """Return True when the nudge actually changed the expression."""
        return self.expression != self.original_expression

    @property
    def summary(self) -> str:
        """One-line human-readable summary."""
        if self.was_modified:
            return (
                f"{self.original_expression!r} nudged by {self.offset_minutes:+d} min "
                f"-> {self.expression!r}"
            )
        return f"{self.original_expression!r} unchanged after nudge"


def _nudge_minute_token(token: str, offset: int) -> str:
    """Shift a single minute token by *offset* minutes (wraps 0-59)."""
    if token == "*":
        return token
    if "/" in token:
        # step expressions like */5 or 0/5 – shift the start only
        parts = token.split("/", 1)
        try:
            start = (int(parts[0]) + offset) % 60
        except ValueError:
            return token
        return f"{start}/{parts[1]}"
    if "-" in token:
        lo, hi = token.split("-", 1)
        try:
            new_lo = (int(lo) + offset) % 60
            new_hi = (int(hi) + offset) % 60
        except ValueError:
            return token
        return f"{new_lo}-{new_hi}"
    if "," in token:
        parts = token.split(",")
        shifted = []
        for p in parts:
            try:
                shifted.append(str((int(p) + offset) % 60))
            except ValueError:
                shifted.append(p)
        return ",".join(shifted)
    try:
        return str((int(token) + offset) % 60)
    except ValueError:
        return token


def nudge(
    expression: str,
    offset_minutes: int,
    *,
    label: Optional[str] = None,
) -> NudgeResult:
    """Shift the minute field of *expression* by *offset_minutes*.

    Only the minute field is adjusted; all other fields are preserved.
    Wrapping is modulo-60.
    """
    expr: CronExpression = parse(expression)
    tokens = expression.split()
    minute_token = tokens[0] if tokens else "*"
    nudged_minute = _nudge_minute_token(minute_token, offset_minutes)
    nudged_tokens = [nudged_minute] + tokens[1:]
    nudged_expression = " ".join(nudged_tokens)
    # Validate by parsing the result
    parse(nudged_expression)
    return NudgeResult(
        expression=nudged_expression,
        offset_minutes=offset_minutes,
        original_expression=expression,
        label=label,
        nudged_tokens=nudged_tokens,
    )
