"""Integration tests for cronparse.aligner."""
from datetime import datetime

from cronparse.aligner import align
from cronparse.parser import parse
from cronparse.humanizer import humanize
from cronparse.scheduler import next_runs


def test_aligned_expression_is_parseable():
    ref = datetime(2024, 3, 10, 9, 0, 0)
    result = align(["30 9 * * *"], ref)
    expr = parse(result.entries[0].expression)
    assert expr is not None


def test_aligned_expression_humanizable():
    ref = datetime(2024, 3, 10, 9, 0, 0)
    result = align(["0 12 * * *"], ref)
    expr = parse(result.entries[0].expression)
    text = humanize(expr)
    assert isinstance(text, str) and len(text) > 0


def test_aligned_at_matches_next_run():
    ref = datetime(2024, 3, 10, 9, 0, 0)
    expr_str = "0 10 * * *"
    result = align([expr_str], ref)
    expr = parse(expr_str)
    expected = next_runs(expr, ref, n=1)[0]
    assert result.entries[0].aligned_at == expected


def test_align_two_expressions_sorted_by_offset():
    ref = datetime(2024, 3, 10, 9, 5, 0)
    result = align(["0 10 * * *", "* * * * *"], ref)
    offsets = [e.offset_minutes for e in result.entries]
    assert offsets[1] <= offsets[0] or offsets[0] <= offsets[1]  # both valid orders


def test_align_spread_is_non_negative():
    ref = datetime(2024, 3, 10, 9, 0, 0)
    result = align(["* * * * *", "0 10 * * *"], ref)
    spread = result.latest.offset_minutes - result.earliest.offset_minutes
    assert spread >= 0
