"""Tests for cronparse.calendar."""
from datetime import datetime, timezone

import pytest

from cronparse.parser import parse
from cronparse.calendar import build_calendar, CalendarCell, CalendarView


@pytest.fixture
def start():
    return datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)


def test_build_calendar_returns_calendar_view(start):
    expr = parse("0 * * * *")
    view = build_calendar(expr, start, days=1, expression_str="0 * * * *")
    assert isinstance(view, CalendarView)


def test_build_calendar_cell_count_matches_hours(start):
    expr = parse("0 * * * *")
    view = build_calendar(expr, start, days=1, expression_str="0 * * * *")
    assert len(view.cells) == 24


def test_build_calendar_every_hour_all_cells_fire(start):
    expr = parse("0 * * * *")
    view = build_calendar(expr, start, days=1, expression_str="0 * * * *")
    assert all(c.fires for c in view.cells)


def test_build_calendar_specific_hour_only_that_cell_fires(start):
    expr = parse("0 9 * * *")
    view = build_calendar(expr, start, days=1, expression_str="0 9 * * *")
    firing = [c for c in view.cells if c.fires]
    assert len(firing) == 1
    assert firing[0].dt.hour == 9


def test_build_calendar_firing_count(start):
    expr = parse("0 9 * * *")
    view = build_calendar(expr, start, days=7, expression_str="0 9 * * *")
    assert view.firing_count == 7


def test_build_calendar_label_propagated(start):
    expr = parse("* * * * *")
    view = build_calendar(expr, start, days=1, expression_str="* * * * *", label="every-min")
    assert view.label == "every-min"


def test_build_calendar_by_day_returns_dict(start):
    expr = parse("0 * * * *")
    view = build_calendar(expr, start, days=3, expression_str="0 * * * *")
    by_day = view.by_day()
    assert isinstance(by_day, dict)
    assert len(by_day) == 3


def test_build_calendar_by_day_each_has_24_cells(start):
    expr = parse("0 * * * *")
    view = build_calendar(expr, start, days=2, expression_str="0 * * * *")
    for cells in view.by_day().values():
        assert len(cells) == 24


def test_calendar_cell_str_fires():
    dt = datetime(2024, 1, 1, 9, 0, tzinfo=timezone.utc)
    cell = CalendarCell(dt=dt, fires=True)
    assert "[X]" in str(cell)


def test_calendar_cell_str_no_fire():
    dt = datetime(2024, 1, 1, 9, 0, tzinfo=timezone.utc)
    cell = CalendarCell(dt=dt, fires=False)
    assert "[.]" in str(cell)


def test_build_calendar_invalid_days_raises(start):
    expr = parse("0 * * * *")
    with pytest.raises(ValueError):
        build_calendar(expr, start, days=0)


def test_build_calendar_expression_str_stored(start):
    expr = parse("30 6 * * 1")
    view = build_calendar(expr, start, days=7, expression_str="30 6 * * 1")
    assert view.expression == "30 6 * * 1"
