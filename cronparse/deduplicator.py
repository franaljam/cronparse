"""Semantic deduplication of cron expressions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .parser import parse
from .normalizer import normalize


@dataclass
class DeduplicateEntry:
    """A single entry in a deduplicated result."""

    expression: str
    label: Optional[str]
    canonical: str
    duplicates: List[str]

    def __str__(self) -> str:
        dups = f" ({len(self.duplicates)} duplicate(s) removed)" if self.duplicates else ""
        label_part = f"[{self.label}] " if self.label else ""
        return f"{label_part}{self.expression}{dups}"


@dataclass
class DeduplicateResult:
    """Result of a deduplication pass over multiple cron expressions."""

    entries: List[DeduplicateEntry] = field(default_factory=list)
    original_count: int = 0
    removed_count: int = 0

    @property
    def kept_count(self) -> int:
        return len(self.entries)

    @property
    def summary(self) -> str:
        return (
            f"{self.kept_count} unique expression(s) kept, "
            f"{self.removed_count} duplicate(s) removed "
            f"(from {self.original_count} total)"
        )

    def __str__(self) -> str:
        return self.summary


def deduplicate(
    expressions: List[str],
    labels: Optional[List[Optional[str]]] = None,
) -> DeduplicateResult:
    """Deduplicate a list of cron expressions by canonical form.

    Two expressions are considered duplicates if they normalise to the same
    canonical string (e.g. ``"0 * * * *"`` and ``"0 */1 * * *"`` are
    semantically equivalent).

    The *first* occurrence of each canonical form is kept; subsequent ones are
    recorded as duplicates on that entry.

    Args:
        expressions: Raw cron expression strings.
        labels: Optional parallel list of labels.  ``None`` entries are allowed.

    Returns:
        A :class:`DeduplicateResult` describing kept and removed expressions.
    """
    if labels is None:
        labels = [None] * len(expressions)
    if len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")

    seen: dict[str, int] = {}  # canonical -> index in entries list
    entries: List[DeduplicateEntry] = []
    removed = 0

    for expr, lbl in zip(expressions, labels):
        try:
            canonical = normalize(parse(expr)).canonical
        except Exception:
            canonical = expr  # fall back to raw string if unparseable

        if canonical in seen:
            entries[seen[canonical]].duplicates.append(expr)
            removed += 1
        else:
            seen[canonical] = len(entries)
            entries.append(
                DeduplicateEntry(
                    expression=expr,
                    label=lbl,
                    canonical=canonical,
                    duplicates=[],
                )
            )

    return DeduplicateResult(
        entries=entries,
        original_count=len(expressions),
        removed_count=removed,
    )
