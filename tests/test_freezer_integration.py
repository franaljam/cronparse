"""Integration tests for cronparse.freezer."""
from __future__ import annotations

from datetime import datetime, timezone

from cronparse.freezer import freeze
from cronparse.humanizer import humanize
from cronparse.parser import parse


def dt(minute: int = 0, hour: int = 0) -> datetime:
    return datetime(2024, 3, 10, hour, minute, 0, tzinfo=timezone.utc)


def test_frozen_expression_is_parseable():
    result = freeze("0 9 * * 1-5", anchor=dt())
    parsed = parse(result.expression)
    assert parsed is not None


def test_frozen_expression_humanizable():
    result = freeze("0 9 * * 1-5", anchor=dt())
    text = humanize(parse(result.expression))
    assert isinstance(text, str)
    assert len(text) > 0


def test_freeze_every_minute_skip_one_resumes_at_next_minute():
    anchor = dt(10, 8)
    result = freeze("* * * * *", anchor=anchor, skip=1, n=1)
    # skipped run is minute 10, resume is minute 11
    assert result.resume_at is not None
    assert result.resume_at.minute == 11


def test_freeze_hourly_skip_two_resumes_at_third_hour():
    anchor = dt(0, 0)
    result = freeze("0 * * * *", anchor=anchor, skip=2, n=3)
    assert result.resume_at is not None
    assert result.resume_at.hour == 2


def test_freeze_runs_after_resume_are_after_resume_at():
    anchor = dt(0, 6)
    result = freeze("* * * * *", anchor=anchor, skip=3, n=4)
    for run in result.runs_after_resume:
        assert run >= result.resume_at
