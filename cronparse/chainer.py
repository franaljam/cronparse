"""cronparse.chainer — Chain multiple cron expressions into a unified schedule.

Allows combining several cron expressions into a single ordered sequence of
firing times, useful for inspecting how multiple jobs interleave over time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterator, List, Optional

from .parser import parse
from .scheduler import iter_runs


@dataclass
class ChainEntry:
    """A single firing event within a chained schedule."""

    index: int
    fired_at: datetime
    expression: str
    label: Optional[str] = None

    def __str__(self) -> str:  # noqa: D401
        tag = f"[{self.label}] " if self.label else ""
        return f"{self.index:>3}. {tag}{self.fired_at.isoformat()} ({self.expression})"


@dataclass
class ChainResult:
    """Ordered sequence of firing events across multiple expressions."""

    entries: List[ChainEntry] = field(default_factory=list)
    expressions: List[str] = field(default_factory=list)
    labels: List[Optional[str]] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Convenience accessors
    # ------------------------------------------------------------------

    @property
    def count(self) -> int:
        """Total number of entries in the chain."""
        return len(self.entries)

    @property
    def first(self) -> Optional[ChainEntry]:
        """Earliest entry, or *None* if the chain is empty."""
        return self.entries[0] if self.entries else None

    @property
    def last(self) -> Optional[ChainEntry]:
        """Latest entry, or *None* if the chain is empty."""
        return self.entries[-1] if self.entries else None

    def by_label(self, label: str) -> List[ChainEntry]:
        """Return all entries that match *label*."""
        return [e for e in self.entries if e.label == label]

    def summary(self) -> str:
        """One-line human-readable summary of the chain."""
        if not self.entries:
            return "Empty chain (no entries)"
        return (
            f"{self.count} events across {len(self.expressions)} expression(s); "
            f"from {self.first.fired_at.isoformat()} to {self.last.fired_at.isoformat()}"
        )

    def __str__(self) -> str:  # noqa: D401
        return self.summary()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _iter_tagged(
    expr_str: str,
    label: Optional[str],
    start: datetime,
    n: int,
) -> Iterator[tuple[datetime, str, Optional[str]]]:
    """Yield *(fired_at, expression, label)* tuples for one expression."""
    expr = parse(expr_str)
    for run in iter_runs(expr, start=start, count=n):
        yield run, expr_str, label


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def chain(
    expressions: List[str],
    start: datetime,
    n: int = 10,
    labels: Optional[List[Optional[str]]] = None,
) -> ChainResult:
    """Merge *n* upcoming runs from each expression into a single sorted chain.

    Parameters
    ----------
    expressions:
        One or more cron expression strings.
    start:
        Datetime from which scheduling begins (inclusive boundary).
    n:
        Number of upcoming runs to collect **per expression** before merging.
    labels:
        Optional list of labels, one per expression.  When supplied its length
        must match *expressions*; use ``None`` elements for unlabelled entries.

    Returns
    -------
    ChainResult
        Entries sorted chronologically; ties are broken by expression order.
    """
    if not expressions:
        return ChainResult(expressions=[], labels=[])

    if labels is None:
        labels = [None] * len(expressions)

    if len(labels) != len(expressions):
        raise ValueError(
            f"labels length ({len(labels)}) must match expressions length ({len(expressions)})"
        )

    # Collect all events from all expressions.
    pool: list[tuple[datetime, int, str, Optional[str]]] = []
    for order, (expr_str, label) in enumerate(zip(expressions, labels)):
        for fired_at, expr, lbl in _iter_tagged(expr_str, label, start, n):
            pool.append((fired_at, order, expr, lbl))

    # Sort by time, then by original expression order to break ties.
    pool.sort(key=lambda t: (t[0], t[1]))

    entries = [
        ChainEntry(index=idx + 1, fired_at=fired_at, expression=expr, label=lbl)
        for idx, (fired_at, _order, expr, lbl) in enumerate(pool)
    ]

    return ChainResult(
        entries=entries,
        expressions=list(expressions),
        labels=list(labels),
    )
