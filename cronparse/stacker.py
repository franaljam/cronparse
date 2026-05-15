"""Stack multiple cron expressions into a unified timeline view."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from cronparse.parser import parse
from cronparse.scheduler import next_runs


@dataclass
class StackEntry:
    """A single firing event in the stacked timeline."""

    expression: str
    label: Optional[str]
    run_at: datetime
    index: int  # position within its own expression's run list

    def __str__(self) -> str:
        tag = self.label or self.expression
        return f"{self.run_at.isoformat()} [{tag}]"


@dataclass
class StackResult:
    """Merged, chronologically sorted timeline of multiple expressions."""

    entries: List[StackEntry] = field(default_factory=list)
    expressions: List[str] = field(default_factory=list)
    labels: List[Optional[str]] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.entries)

    @property
    def first(self) -> Optional[StackEntry]:
        return self.entries[0] if self.entries else None

    @property
    def last(self) -> Optional[StackEntry]:
        return self.entries[-1] if self.entries else None

    def by_label(self, label: str) -> List[StackEntry]:
        """Return entries matching a specific label."""
        return [e for e in self.entries if e.label == label]

    def summary(self) -> str:
        if not self.entries:
            return "Empty stack."
        return (
            f"{self.count} events across {len(self.expressions)} expression(s); "
            f"first={self.first.run_at.isoformat()}, last={self.last.run_at.isoformat()}"
        )


def stack(
    expressions: List[str],
    *,
    n: int = 5,
    start: Optional[datetime] = None,
    labels: Optional[List[Optional[str]]] = None,
) -> StackResult:
    """Merge *n* next runs from each expression into one sorted timeline.

    Parameters
    ----------
    expressions:
        List of cron expression strings.
    n:
        Number of upcoming runs to collect per expression.
    start:
        Reference datetime (defaults to ``datetime.utcnow()``).
    labels:
        Optional list of labels aligned with *expressions*.

    Returns
    -------
    StackResult
        Chronologically sorted collection of firing events.
    """
    if labels is not None and len(labels) != len(expressions):
        raise ValueError("labels length must match expressions length")

    resolved_labels: List[Optional[str]] = (
        labels if labels is not None else [None] * len(expressions)
    )

    if start is None:
        start = datetime.utcnow()

    all_entries: List[StackEntry] = []

    for expr_str, lbl in zip(expressions, resolved_labels):
        parsed = parse(expr_str)
        runs = next_runs(parsed, n=n, start=start)
        for idx, run_at in enumerate(runs, start=1):
            all_entries.append(
                StackEntry(expression=expr_str, label=lbl, run_at=run_at, index=idx)
            )

    all_entries.sort(key=lambda e: e.run_at)

    return StackResult(
        entries=all_entries,
        expressions=list(expressions),
        labels=list(resolved_labels),
    )
