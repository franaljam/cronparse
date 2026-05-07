"""Heatmap: generate hour-of-day x day-of-week firing frequency grids."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from cronparse.parser import CronExpression, parse
from cronparse.scheduler import iter_runs

import datetime


@dataclass
class HeatmapCell:
    hour: int
    weekday: int  # 0=Monday … 6=Sunday
    count: int

    def __str__(self) -> str:
        return f"hour={self.hour} weekday={self.weekday} count={self.count}"


@dataclass
class HeatmapResult:
    expression: str
    label: Optional[str]
    # grid[weekday][hour] = count
    grid: List[List[int]]
    sample_days: int

    # ------------------------------------------------------------------
    def cell(self, weekday: int, hour: int) -> HeatmapCell:
        return HeatmapCell(hour=hour, weekday=weekday, count=self.grid[weekday][hour])

    def peak(self) -> HeatmapCell:
        """Return the cell with the highest firing count."""
        best = HeatmapCell(0, 0, -1)
        for wd in range(7):
            for h in range(24):
                if self.grid[wd][h] > best.count:
                    best = HeatmapCell(hour=h, weekday=wd, count=self.grid[wd][h])
        return best

    def total_fires(self) -> int:
        return sum(self.grid[wd][h] for wd in range(7) for h in range(24))

    def summary(self) -> str:
        p = self.peak()
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        tag = f" ({self.label})" if self.label else ""
        return (
            f"{self.expression}{tag}: {self.total_fires()} fires over "
            f"{self.sample_days} days, peak {days[p.weekday]} {p.hour:02d}:xx "
            f"({p.count} fires)"
        )


def build_heatmap(
    expression: str,
    *,
    sample_days: int = 7,
    start: Optional[datetime.datetime] = None,
    label: Optional[str] = None,
) -> HeatmapResult:
    """Build a 7×24 firing-frequency heatmap for *expression*."""
    if sample_days < 1:
        raise ValueError("sample_days must be >= 1")

    expr: CronExpression = parse(expression)
    origin = start or datetime.datetime(2024, 1, 1, 0, 0, 0)
    end = origin + datetime.timedelta(days=sample_days)

    # grid[weekday 0-6][hour 0-23]
    grid: List[List[int]] = [[0] * 24 for _ in range(7)]

    total_minutes = sample_days * 24 * 60
    for dt in iter_runs(expr, start=origin, count=total_minutes):
        if dt >= end:
            break
        wd = dt.weekday()  # 0=Monday
        grid[wd][dt.hour] += 1

    return HeatmapResult(
        expression=expression,
        label=label,
        grid=grid,
        sample_days=sample_days,
    )
