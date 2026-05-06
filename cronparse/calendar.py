"""Calendar view: map cron runs onto a weekly or monthly grid."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from cronparse.scheduler import next_runs
from cronparse.parser import CronExpression


@dataclass
class CalendarCell:
    """A single time-slot cell in the calendar grid."""
    dt: datetime
    fires: bool
    label: Optional[str] = None

    def __str__(self) -> str:  # pragma: no cover
        mark = "X" if self.fires else "."
        return f"{self.dt.strftime('%Y-%m-%d %H:%M')} [{mark}]"


@dataclass
class CalendarView:
    """A collection of cells spanning a time window."""
    expression: str
    label: Optional[str]
    cells: List[CalendarCell] = field(default_factory=list)

    @property
    def firing_count(self) -> int:
        return sum(1 for c in self.cells if c.fires)

    def by_day(self) -> Dict[str, List[CalendarCell]]:
        """Group cells by date string (YYYY-MM-DD)."""
        result: Dict[str, List[CalendarCell]] = {}
        for cell in self.cells:
            key = cell.dt.strftime("%Y-%m-%d")
            result.setdefault(key, []).append(cell)
        return result


def build_calendar(
    expr: CronExpression,
    start: datetime,
    days: int = 7,
    expression_str: str = "",
    label: Optional[str] = None,
) -> CalendarView:
    """Build a CalendarView for *expr* covering *days* days from *start*.

    Resolution is one cell per hour.
    """
    if days < 1 or days > 366:
        raise ValueError("days must be between 1 and 366")

    end = start + timedelta(days=days)
    # Collect all firing datetimes in window
    runs = set(
        r.replace(second=0, microsecond=0)
        for r in next_runs(expr, start=start, n=days * 24 * 60)
        if r < end
    )

    cells: List[CalendarCell] = []
    cursor = start.replace(minute=0, second=0, microsecond=0)
    while cursor < end:
        # Check if any run falls within this hour
        fires = any(
            cursor <= r < cursor + timedelta(hours=1) for r in runs
        )
        cells.append(CalendarCell(dt=cursor, fires=fires, label=label))
        cursor += timedelta(hours=1)

    return CalendarView(expression=expression_str, label=label, cells=cells)
