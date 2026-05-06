"""Reduce a list of cron expressions to a minimal equivalent set.

Two expressions are considered duplicates if their normalized canonical
forms are identical.  The reducer also optionally merges expressions that
fire at the same frequency into a human-readable summary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from cronparse.normalizer import normalize, are_equivalent
from cronparse.humanizer import humanize
from cronparse.parser import parse


@dataclass
class ReduceResult:
    """Outcome of a reduce operation."""

    original_count: int
    reduced: List[str]
    removed: List[str]
    labels: List[Optional[str]]

    @property
    def reduction_count(self) -> int:
        return self.original_count - len(self.reduced)

    def summary(self) -> str:
        lines = [
            f"Original : {self.original_count} expression(s)",
            f"Reduced  : {len(self.reduced)} expression(s)",
            f"Removed  : {self.reduction_count} duplicate(s)",
        ]
        for expr, label in zip(self.reduced, self.labels):
            tag = f" [{label}]" if label else ""
            lines.append(f"  {expr}{tag}  — {humanize(parse(expr))}")
        return "\n".join(lines)


def reduce(
    expressions: List[str],
    labels: Optional[List[Optional[str]]] = None,
) -> ReduceResult:
    """Remove duplicate cron expressions from *expressions*.

    Duplicates are detected by comparing normalized canonical strings so
    that semantically identical but syntactically different expressions
    (e.g. ``*/1 * * * *`` and ``* * * * *``) are collapsed.

    Parameters
    ----------
    expressions:
        Raw cron expression strings to deduplicate.
    labels:
        Optional list of labels aligned with *expressions*.  Must be the
        same length when provided.

    Returns
    -------
    ReduceResult
    """
    if labels is not None and len(labels) != len(expressions):
        raise ValueError(
            f"labels length {len(labels)} does not match "
            f"expressions length {len(expressions)}"
        )

    effective_labels: List[Optional[str]] = (
        labels if labels is not None else [None] * len(expressions)
    )

    seen: dict[str, int] = {}  # canonical -> first index in reduced lists
    reduced_exprs: List[str] = []
    reduced_labels: List[Optional[str]] = []
    removed: List[str] = []

    for expr, label in zip(expressions, effective_labels):
        canonical = normalize(parse(expr)).canonical
        if canonical in seen:
            removed.append(expr)
        else:
            seen[canonical] = len(reduced_exprs)
            reduced_exprs.append(expr)
            reduced_labels.append(label)

    return ReduceResult(
        original_count=len(expressions),
        reduced=reduced_exprs,
        removed=removed,
        labels=reduced_labels,
    )
