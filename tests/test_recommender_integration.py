"""Integration tests: recommender output is parseable and humanizable."""

import pytest
from cronparse.recommender import recommend
from cronparse.parser import parse
from cronparse.humanizer import humanize
from cronparse.scheduler import next_runs
from datetime import datetime, timezone


_QUERIES = [
    "every minute",
    "every hour",
    "daily",
    "every weekday",
    "every 15 minutes",
    "monthly",
]


@pytest.mark.parametrize("query", _QUERIES)
def test_recommended_expression_is_parseable(query):
    result = recommend(query)
    assert result.best is not None
    expr = parse(result.best.expression)
    assert expr is not None


@pytest.mark.parametrize("query", _QUERIES)
def test_recommended_expression_humanizable(query):
    result = recommend(query)
    expr = parse(result.best.expression)
    text = humanize(expr)
    assert isinstance(text, str)
    assert len(text) > 0


@pytest.mark.parametrize("query", _QUERIES)
def test_recommended_expression_schedulable(query):
    result = recommend(query)
    expr = parse(result.best.expression)
    start = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
    runs = next_runs(expr, start, n=3)
    assert len(runs) == 3


def test_human_field_matches_humanizer_output():
    result = recommend("every hour")
    rec = result.best
    parsed = parse(rec.expression)
    expected = humanize(parsed)
    assert rec.human == expected


def test_recommend_twice_a_day_schedules_correctly():
    result = recommend("twice a day")
    assert result.best is not None
    expr = parse(result.best.expression)
    start = datetime(2024, 6, 1, 0, 0, tzinfo=timezone.utc)
    runs = next_runs(expr, start, n=4)
    # Should fire at 00:00 and 12:00 each day
    assert len(runs) == 4
    hours = sorted({r.hour for r in runs})
    assert 0 in hours
    assert 12 in hours
