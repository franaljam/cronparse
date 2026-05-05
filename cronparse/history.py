"""Track and inspect past run history for cron expressions."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from cronparse.parser import CronExpression, parse
from cronparse.scheduler import iter_runs
from cronparse.humanizer import humanize


@dataclass
class RunRecord:
    """A single recorded run timestamp."""

    expression: str
    scheduled_at: datetime
    label: Optional[str] = None

    def __str__(self) -> str:
        label_part = f" [{self.label}]" if self.label else ""
        return f"{self.scheduled_at.isoformat()}{label_part} — {self.expression}"


@dataclass
class RunHistory:
    """Collection of run records for a cron expression."""

    expression: str
    records: List[RunRecord] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.records)

    @property
    def latest(self) -> Optional[RunRecord]:
        return self.records[-1] if self.records else None

    @property
    def earliest(self) -> Optional[RunRecord]:
        return self.records[0] if self.records else None

    def summary(self) -> str:
        if not self.records:
            return f"No history for '{self.expression}'"
        return (
            f"Expression : {self.expression}\n"
            f"Human      : {humanize(parse(self.expression))}\n"
            f"Runs       : {self.count}\n"
            f"Earliest   : {self.earliest.scheduled_at.isoformat()}\n"
            f"Latest     : {self.latest.scheduled_at.isoformat()}"
        )


def build_history(
    expression: str,
    start: datetime,
    n: int,
    label: Optional[str] = None,
) -> RunHistory:
    """Build a RunHistory by generating `n` scheduled runs from `start`."""
    expr: CronExpression = parse(expression)
    history = RunHistory(expression=expression)
    for dt in iter_runs(expr, start):
        history.records.append(
            RunRecord(expression=expression, scheduled_at=dt, label=label)
        )
        if len(history.records) >= n:
            break
    return history


def filter_history(
    history: RunHistory,
    after: Optional[datetime] = None,
    before: Optional[datetime] = None,
) -> RunHistory:
    """Return a new RunHistory containing only records within the given window."""
    records = history.records
    if after:
        records = [r for r in records if r.scheduled_at >= after]
    if before:
        records = [r for r in records if r.scheduled_at <= before]
    result = RunHistory(expression=history.expression)
    result.records = records
    return result
