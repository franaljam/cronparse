"""Integration helpers that combine alias resolution with parsing and humanizing."""

from typing import List

from cronparse.alias import resolve
from cronparse.humanizer import humanize
from cronparse.parser import CronExpression, parse
from cronparse.scheduler import next_runs


def parse_with_alias(expression: str) -> CronExpression:
    """Resolve any @-alias then parse the resulting cron expression."""
    resolved = resolve(expression)
    return parse(resolved)


def humanize_alias(expression: str) -> str:
    """Return a human-readable description, resolving @-aliases first."""
    expr = parse_with_alias(expression)
    return humanize(expr)


def next_runs_alias(
    expression: str,
    n: int = 5,
    *,
    start=None,
    timezone: str = "UTC",
) -> List:
    """Compute the next *n* run times for an expression or @-alias.

    Parameters
    ----------
    expression:
        A standard cron string or an @-alias such as ``@daily``.
    n:
        Number of upcoming run times to return.
    start:
        Datetime to start searching from (defaults to ``datetime.utcnow()``).
    timezone:
        IANA timezone name used to localise results.
    """
    from datetime import datetime, timezone as _tz

    if start is None:
        start = datetime.now(_tz.utc)

    expr = parse_with_alias(expression)
    return next_runs(expr, n=n, start=start)
