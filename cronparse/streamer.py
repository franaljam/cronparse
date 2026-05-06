"""Streaming cron run generator with filtering and limiting support."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Iterator, List, Optional

from .parser import parse
from .scheduler import iter_runs
from .timezone import get_timezone, localize


@dataclass
class StreamConfig:
    """Configuration for a cron run stream."""

    expression: str
    start: datetime
    max_count: Optional[int] = None
    end: Optional[datetime] = None
    timezone: Optional[str] = None
    filter_fn: Optional[Callable[[datetime], bool]] = None
    label: Optional[str] = None


@dataclass
class StreamResult:
    """A single result from a cron stream."""

    index: int
    run_time: datetime
    label: Optional[str] = None

    def __str__(self) -> str:
        prefix = f"[{self.label}] " if self.label else ""
        return f"{prefix}#{self.index}: {self.run_time.isoformat()}"


def stream(
    config: StreamConfig,
) -> Iterator[StreamResult]:
    """Yield StreamResult objects for each scheduled run matching the config."""
    expr = parse(config.expression)
    tz = get_timezone(config.timezone) if config.timezone else None
    start = localize(config.start, tz) if tz and config.start.tzinfo is None else config.start

    count = 0
    for run_time in iter_runs(expr, start):
        if config.end is not None and run_time > config.end:
            break
        if config.max_count is not None and count >= config.max_count:
            break
        if config.filter_fn is not None and not config.filter_fn(run_time):
            continue
        yield StreamResult(index=count + 1, run_time=run_time, label=config.label)
        count += 1


def collect(config: StreamConfig) -> List[StreamResult]:
    """Collect all stream results into a list."""
    return list(stream(config))
