"""Compare multiple cron expressions by their schedule frequency and overlap."""

from dataclasses import dataclass, field
from typing import List, Tuple
from datetime import datetime, timezone

from cronparse.parser import CronExpression, parse
from cronparse.scheduler import next_runs


@dataclass
class OverlapResult:
    expressions: Tuple[str, str]
    shared_times: List[datetime]

    def has_overlap(self) -> bool:
        return len(self.shared_times) > 0

    def __str__(self) -> str:
        if not self.has_overlap():
            return f"No overlap between '{self.expressions[0]}' and '{self.expressions[1]}'"
        count = len(self.shared_times)
        first = self.shared_times[0].isoformat()
        return (
            f"'{self.expressions[0]}' and '{self.expressions[1]}' overlap "
            f"{count} time(s) in window; first at {first}"
        )


@dataclass
class FrequencyInfo:
    expression: str
    runs_per_hour: float
    runs_per_day: float

    def __str__(self) -> str:
        return (
            f"'{self.expression}': "
            f"{self.runs_per_hour:.2f} runs/hour, "
            f"{self.runs_per_day:.2f} runs/day"
        )


def frequency(expr: str) -> FrequencyInfo:
    """Estimate how often a cron expression fires per hour and per day."""
    parsed = parse(expr)
    minute_count = len(parsed.minute)
    hour_count = len(parsed.hour)
    runs_per_day = minute_count * hour_count
    runs_per_hour = minute_count
    return FrequencyInfo(
        expression=expr,
        runs_per_hour=float(runs_per_hour),
        runs_per_day=float(runs_per_day),
    )


def find_overlap(
    expr_a: str,
    expr_b: str,
    start: datetime | None = None,
    window: int = 1440,
) -> OverlapResult:
    """Find times when two cron expressions fire at the same minute within a window.

    Args:
        expr_a: First cron expression string.
        expr_b: Second cron expression string.
        start: Start datetime (UTC). Defaults to now.
        window: Number of minutes to look ahead.
    """
    if start is None:
        start = datetime.now(tz=timezone.utc)

    runs_a = set(next_runs(parse(expr_a), start, n=window))
    runs_b = set(next_runs(parse(expr_b), start, n=window))
    shared = sorted(runs_a & runs_b)
    return OverlapResult(expressions=(expr_a, expr_b), shared_times=shared)


def rank_by_frequency(expressions: List[str]) -> List[FrequencyInfo]:
    """Rank a list of cron expressions from most to least frequent."""
    infos = [frequency(e) for e in expressions]
    return sorted(infos, key=lambda f: f.runs_per_day, reverse=True)
