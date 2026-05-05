"""Tests for cronparse.scheduler."""

from datetime import datetime

import pytest

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo  # type: ignore

from cronparse.scheduler import next_runs, iter_runs

UTC = zoneinfo.ZoneInfo("UTC")


def dt(*args, tz=UTC):
    """Shorthand for creating an aware datetime."""
    return datetime(*args, tzinfo=tz)


# ---------------------------------------------------------------------------
# next_runs
# ---------------------------------------------------------------------------

def test_next_runs_returns_n_results():
    runs = next_runs("* * * * *", n=5, after=dt(2024, 1, 1, 0, 0))
    assert len(runs) == 5


def test_every_minute_increments_by_one():
    after = dt(2024, 1, 1, 12, 0)
    runs = next_runs("* * * * *", n=3, after=after)
    assert runs[0] == dt(2024, 1, 1, 12, 1)
    assert runs[1] == dt(2024, 1, 1, 12, 2)
    assert runs[2] == dt(2024, 1, 1, 12, 3)


def test_specific_minute_and_hour():
    after = dt(2024, 1, 1, 0, 0)
    runs = next_runs("30 9 * * *", n=2, after=after)
    assert runs[0] == dt(2024, 1, 1, 9, 30)
    assert runs[1] == dt(2024, 1, 2, 9, 30)


def test_step_expression():
    after = dt(2024, 3, 15, 8, 0)
    runs = next_runs("*/15 * * * *", n=4, after=after)
    assert runs[0] == dt(2024, 3, 15, 8, 15)
    assert runs[1] == dt(2024, 3, 15, 8, 30)
    assert runs[2] == dt(2024, 3, 15, 8, 45)
    assert runs[3] == dt(2024, 3, 15, 9, 0)


def test_specific_day_of_month():
    after = dt(2024, 1, 1, 0, 0)
    runs = next_runs("0 0 15 * *", n=3, after=after)
    assert runs[0] == dt(2024, 1, 15, 0, 0)
    assert runs[1] == dt(2024, 2, 15, 0, 0)
    assert runs[2] == dt(2024, 3, 15, 0, 0)


def test_specific_month():
    after = dt(2024, 1, 1, 0, 0)
    runs = next_runs("0 12 1 6 *", n=2, after=after)
    assert runs[0] == dt(2024, 6, 1, 12, 0)
    assert runs[1] == dt(2025, 6, 1, 12, 0)


def test_weekday_monday():
    # 2024-01-01 is a Monday (cron weekday 1)
    after = dt(2024, 1, 1, 0, 0)
    runs = next_runs("0 0 * * 1", n=2, after=after)
    assert runs[0].weekday() == 0  # Python Monday == 0
    assert runs[1].weekday() == 0
    assert (runs[1] - runs[0]).days == 7


def test_timezone_aware_output():
    runs = next_runs("0 9 * * *", n=1, timezone="America/New_York")
    assert runs[0].tzinfo is not None
    assert str(runs[0].tzinfo) == "America/New_York"


def test_naive_after_gets_tz_attached():
    naive = datetime(2024, 6, 1, 0, 0)
    runs = next_runs("0 6 * * *", n=1, after=naive, timezone="Europe/London")
    assert runs[0].tzinfo is not None


# ---------------------------------------------------------------------------
# iter_runs
# ---------------------------------------------------------------------------

def test_iter_runs_is_infinite():
    after = dt(2024, 1, 1, 0, 0)
    gen = iter_runs("* * * * *", after=after)
    results = [next(gen) for _ in range(10)]
    assert len(results) == 10
    assert results[-1] == dt(2024, 1, 1, 0, 10)


def test_iter_runs_consistent_with_next_runs():
    after = dt(2024, 5, 10, 8, 0)
    expr = "*/5 14 * * *"
    from_next = next_runs(expr, n=6, after=after)
    gen = iter_runs(expr, after=after)
    from_iter = [next(gen) for _ in range(6)]
    assert from_next == from_iter
