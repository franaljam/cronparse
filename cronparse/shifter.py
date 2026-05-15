"""Shifter: shift all firing times of a cron expression by a fixed minute offset."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from cronparse.parser import parse, CronExpression


@dataclass
class ShiftResult:
    """Result of shifting a cron expression by a minute offset."""

    original_expression: str
    shifted_expression: str
    offset_minutes: int
    label: Optional[str] = None
    was_modified: bool = False

    def __str__(self) -> str:  # noqa: D401
        tag = f"[{self.label}] " if self.label else ""
        return (
            f"{tag}{self.original_expression} "
            f"shifted by {self.offset_minutes:+d} min -> {self.shifted_expression}"
        )

    def summary(self) -> str:
        """Return a short human-readable summary of the shift."""
        if not self.was_modified:
            return f"{self.original_expression}: no change (offset 0)"
        return str(self)


def _shift_token(token: str, offset: int, lo: int, hi: int) -> str:
    """Shift a single cron token (minute or hour) by *offset* within [lo, hi]."""
    span = hi - lo + 1
    if token == "*":
        return token
    # list
    if "," in token:
        parts = token.split(",")
        return ",".join(_shift_token(p, offset, lo, hi) for p in parts)
    # range  e.g. 10-20
    if "-" in token and "/" not in token:
        start, end = token.split("-", 1)
        new_start = (int(start) - lo + offset) % span + lo
        new_end = (int(end) - lo + offset) % span + lo
        return f"{new_start}-{new_end}"
    # step  e.g. */5 or 0/5
    if "/" in token:
        base, step = token.split("/", 1)
        if base == "*":
            return token
        new_base = (int(base) - lo + offset) % span + lo
        return f"{new_base}/{step}"
    # plain integer
    new_val = (int(token) - lo + offset) % span + lo
    return str(new_val)


def shift(
    expression: str,
    offset_minutes: int,
    *,
    label: Optional[str] = None,
) -> ShiftResult:
    """Shift the minute field of *expression* by *offset_minutes*.

    Only the minute field is shifted; all other fields are preserved.
    Wrapping is handled modulo 60.
    """
    expr: CronExpression = parse(expression)
    tokens = expression.split()
    minute_token = tokens[0]

    if offset_minutes == 0 or minute_token == "*":
        return ShiftResult(
            original_expression=expression,
            shifted_expression=expression,
            offset_minutes=offset_minutes,
            label=label,
            was_modified=False,
        )

    new_minute = _shift_token(minute_token, offset_minutes, 0, 59)
    tokens[0] = new_minute
    shifted = " ".join(tokens)

    return ShiftResult(
        original_expression=expression,
        shifted_expression=shifted,
        offset_minutes=offset_minutes,
        label=label,
        was_modified=(shifted != expression),
    )


def shift_many(
    expressions: list[str],
    offset_minutes: int,
    *,
    labels: Optional[list[str]] = None,
) -> list[ShiftResult]:
    """Shift multiple expressions by the same offset."""
    if labels is not None and len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")
    return [
        shift(
            expr,
            offset_minutes,
            label=labels[i] if labels else None,
        )
        for i, expr in enumerate(expressions)
    ]
