"""Tests for cronparse.ranker."""

import pytest
from cronparse.ranker import rank, RankEntry, _runs_per_day, _specificity
from cronparse.parser import parse


def test_rank_returns_list_of_rank_entries():
    result = rank(["* * * * *", "0 * * * *"])
    assert isinstance(result, list)
    assert all(isinstance(r, RankEntry) for r in result)


def test_rank_assigns_rank_numbers():
    result = rank(["* * * * *", "0 0 * * *"])
    ranks = [r.rank for r in result]
    assert sorted(ranks) == list(range(1, len(result) + 1))


def test_rank_every_minute_is_most_frequent():
    result = rank(["0 0 * * *", "* * * * *", "0 * * * *"])
    # most frequent first (default)
    assert result[0].expression == "* * * * *"


def test_rank_reverse_puts_least_frequent_first():
    result = rank(["* * * * *", "0 0 * * *"], reverse=True)
    assert result[0].expression == "0 0 * * *"


def test_rank_label_propagated():
    result = rank(["0 0 * * *"], labels=["midnight"])
    assert result[0].label == "midnight"


def test_rank_label_length_mismatch_raises():
    with pytest.raises(ValueError, match="labels length"):
        rank(["* * * * *", "0 * * * *"], labels=["only-one"])


def test_runs_per_day_every_minute():
    expr = parse("* * * * *")
    assert _runs_per_day(expr) == 60 * 24


def test_runs_per_day_hourly():
    expr = parse("0 * * * *")
    assert _runs_per_day(expr) == 1 * 24


def test_runs_per_day_daily():
    expr = parse("0 0 * * *")
    assert _runs_per_day(expr) == 1.0


def test_specificity_all_wildcards_is_zero():
    expr = parse("* * * * *")
    assert _specificity(expr) == 0


def test_specificity_fully_specific():
    expr = parse("30 6 15 6 1")
    assert _specificity(expr) == 5


def test_specificity_partial():
    expr = parse("0 9 * * 1")
    # minute(0)=specific, hour(9)=specific, dom=wildcard, month=wildcard, dow(1)=specific
    assert _specificity(expr) == 3


def test_rank_entry_str_contains_rank():
    result = rank(["0 0 * * *"])
    assert "[1]" in str(result[0])


def test_rank_entry_str_contains_runs_per_day():
    result = rank(["* * * * *"])
    s = str(result[0])
    assert "runs/day" in s
