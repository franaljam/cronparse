"""Zip multiple cron expressions together, pairing their next run times."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple

from .parser import parse
from .scheduler import next_runs


@dataclass
class ZipEntry:
    index: int
    runs: List[Tuple[str, datetime]]

    def __str__(self) -> str:
        parts = ", ".join(f"{label}={dt.isoformat()}" for label, dt in self.runs)
        return f"ZipEntry(index={self.index}, [{parts}])"


@dataclass
class ZipResult:
    expressions: List[str]
    labels: List[str]
    entries: List[ZipEntry]
    n: int

    def count(self) -> int:
        return len(self.entries)

    def first(self) -> Optional[ZipEntry]:
        return self.entries[0] if self.entries else None

    def last(self) -> Optional[ZipEntry]:
        return self.entries[-1] if self.entries else None

    def __str__(self) -> str:
        return f"ZipResult(expressions={len(self.expressions)}, entries={self.count()})"


def zip_runs(
    expressions: List[str],
    anchor: datetime,
    n: int = 5,
    labels: Optional[List[str]] = None,
) -> ZipResult:
    """Pair the next *n* run times across multiple cron expressions.

    Each ZipEntry at index *i* contains the i-th next run for every expression.
    """
    if not expressions:
        return ZipResult(expressions=[], labels=[], entries=[], n=n)

    if labels is None:
        labels = [f"expr{i + 1}" for i in range(len(expressions))]

    if len(labels) != len(expressions):
        raise ValueError(
            f"labels length ({len(labels)}) must match expressions length ({len(expressions)})"
        )

    parsed = [parse(expr) for expr in expressions]
    run_lists = [next_runs(p, anchor, n) for p in parsed]

    entries: List[ZipEntry] = []
    for i in range(n):
        row: List[Tuple[str, datetime]] = []
        for label, runs in zip(labels, run_lists):
            if i < len(runs):
                row.append((label, runs[i]))
        if row:
            entries.append(ZipEntry(index=i + 1, runs=row))

    return ZipResult(expressions=expressions, labels=labels, entries=entries, n=n)
