"""Next-run scheduler: compute upcoming execution times for a cron expression."""

from datetime import datetime, timedelta
from typing import Iterator, List, Optional

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo  # type: ignore

from .parser import CronExpression, parse


def _next_from(
    expr: CronExpression,
    after: datetime,
) -> datetime:
    """Return the first datetime >= (after + 1 minute) that matches *expr*."""
    # Advance by one minute so we never return the same instant twice.
    candidate = after.replace(second=0, microsecond=0) + timedelta(minutes=1)

    # Safety cap: search at most 4 years ahead to avoid infinite loops.
    limit = candidate + timedelta(days=366 * 4)

    while candidate < limit:
        if candidate.month not in expr.months:
            # Jump to the first day of the next valid month.
            candidate = candidate.replace(day=1, hour=0, minute=0)
            candidate += timedelta(days=32)
            candidate = candidate.replace(day=1)
            continue

        if candidate.day not in expr.days:
            candidate = candidate.replace(hour=0, minute=0) + timedelta(days=1)
            continue

        # weekday(): Monday=0 … Sunday=6; cron: Sunday=0 … Saturday=6
        cron_weekday = (candidate.weekday() + 1) % 7
        if cron_weekday not in expr.weekdays:
            candidate = candidate.replace(hour=0, minute=0) + timedelta(days=1)
            continue

        if candidate.hour not in expr.hours:
            candidate = candidate.replace(minute=0) + timedelta(hours=1)
            continue

        if candidate.minute not in expr.minutes:
            candidate += timedelta(minutes=1)
            continue

        return candidate

    raise ValueError("No matching datetime found within the search window.")


def next_runs(
    expression: str,
    n: int = 5,
    after: Optional[datetime] = None,
    timezone: str = "UTC",
) -> List[datetime]:
    """Return the next *n* run-times for *expression* in *timezone*.

    Parameters
    ----------
    expression:
        Standard five-field cron expression.
    n:
        Number of upcoming datetimes to return.
    after:
        Starting point (timezone-aware or naive).  Defaults to *now*.
    timezone:
        IANA timezone name, e.g. ``"America/New_York"``.
    """
    tz = zoneinfo.ZoneInfo(timezone)
    expr: CronExpression = parse(expression)

    if after is None:
        after = datetime.now(tz=tz)
    elif after.tzinfo is None:
        after = after.replace(tzinfo=tz)

    results: List[datetime] = []
    current = after
    for _ in range(n):
        current = _next_from(expr, current).replace(tzinfo=tz)
        results.append(current)

    return results


def iter_runs(
    expression: str,
    after: Optional[datetime] = None,
    timezone: str = "UTC",
) -> Iterator[datetime]:
    """Infinite iterator of run-times for *expression*."""
    tz = zoneinfo.ZoneInfo(timezone)
    expr: CronExpression = parse(expression)

    if after is None:
        after = datetime.now(tz=tz)
    elif after.tzinfo is None:
        after = after.replace(tzinfo=tz)

    current = after
    while True:
        current = _next_from(expr, current).replace(tzinfo=tz)
        yield current
