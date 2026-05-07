"""Integration tests: rewinder output feeds into other modules."""

from datetime import datetime

from cronparse.rewinder import rewind
from cronparse.humanizer import humanize
from cronparse.parser import parse
from cronparse.matcher import match


def test_rewound_runs_match_expression():
    """Every past run returned by rewind should match the expression."""
    expr_str = "0 9 * * 1"
    anchor = datetime(2024, 6, 17, 9, 0, 0)  # Monday 09:00
    result = rewind(expr_str, before=anchor, n=3)
    for run in result.runs:
        m = match(expr_str, run)
        assert m.matched, f"{run} did not match {expr_str}"


def test_rewound_expression_is_parseable():
    result = rewind("*/15 * * * *", before=datetime(2024, 6, 15, 12, 0), n=4)
    expr = parse(result.expression)
    assert expr is not None


def test_rewound_expression_humanizable():
    result = rewind("0 0 * * *", before=datetime(2024, 6, 15, 8, 0), n=2)
    human = humanize(result.expression)
    assert isinstance(human, str)
    assert len(human) > 0


def test_rewind_every_minute_count_matches_n():
    for n in (1, 3, 7):
        result = rewind("* * * * *", before=datetime(2024, 6, 15, 6, 0), n=n)
        assert result.count == n


def test_rewind_hourly_runs_spaced_one_hour_apart():
    from datetime import timedelta
    anchor = datetime(2024, 6, 15, 12, 0)
    result = rewind("0 * * * *", before=anchor, n=3)
    assert result.count == 3
    for i in range(len(result.runs) - 1):
        gap = result.runs[i] - result.runs[i + 1]
        assert gap == timedelta(hours=1)
