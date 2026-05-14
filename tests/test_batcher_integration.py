"""Integration tests for cronparse.batcher."""

from datetime import datetime

from cronparse.batcher import batch
from cronparse.humanizer import humanize
from cronparse.parser import parse


def test_batched_expression_is_parseable():
    result = batch("*/15 * * * *", datetime(2024, 3, 1, 0, 0), num_windows=4, batch_minutes=60)
    expr = parse(result.expression)
    assert expr is not None


def test_batched_expression_humanizable():
    result = batch("0 */2 * * *", datetime(2024, 3, 1, 0, 0), num_windows=3, batch_minutes=120)
    human = humanize(parse(result.expression))
    assert isinstance(human, str)
    assert len(human) > 0


def test_batch_runs_are_datetimes():
    result = batch("* * * * *", datetime(2024, 1, 1, 0, 0), num_windows=2, batch_minutes=5)
    for w in result.windows:
        for r in w.runs:
            assert isinstance(r, datetime)


def test_batch_runs_fall_within_window():
    from datetime import timedelta
    start = datetime(2024, 6, 1, 12, 0)
    result = batch("* * * * *", start, num_windows=3, batch_minutes=60)
    for w in result.windows:
        for r in w.runs:
            assert w.start <= r < w.end


def test_batch_step_expression_distributes_evenly():
    start = datetime(2024, 1, 1, 0, 0)
    result = batch("*/30 * * * *", start, num_windows=4, batch_minutes=60)
    for w in result.windows:
        # Every 30 minutes = 2 runs per hour
        assert w.count == 2
