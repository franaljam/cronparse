"""Tests for cronparse.sampler."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from cronparse.sampler import SampleResult, sample, sample_many


def dt(year=2024, month=1, day=1, hour=0, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)


START = dt()
END = dt(hour=2)  # 2-hour window => 120 possible minutes


def test_sample_returns_sample_result():
    result = sample("* * * * *", START, END, n=5)
    assert isinstance(result, SampleResult)


def test_sample_stores_expression():
    result = sample("* * * * *", START, END, n=5)
    assert result.expression == "* * * * *"


def test_sample_stores_start_and_end():
    result = sample("* * * * *", START, END, n=5)
    assert result.start == START
    assert result.end == END


def test_sample_label_none_by_default():
    result = sample("* * * * *", START, END, n=5)
    assert result.label is None


def test_sample_label_propagated():
    result = sample("* * * * *", START, END, n=5, label="my-job")
    assert result.label == "my-job"


def test_sample_count_at_most_n():
    result = sample("* * * * *", START, END, n=10)
    assert result.count <= 10


def test_sample_every_minute_n_equals_requested():
    result = sample("* * * * *", START, END, n=10)
    assert result.count == 10


def test_sample_runs_within_window():
    result = sample("* * * * *", START, END, n=20)
    for run in result.runs:
        assert START <= run < END


def test_sample_runs_are_sorted():
    result = sample("* * * * *", START, END, n=15)
    assert result.runs == sorted(result.runs)


def test_sample_seed_reproducible():
    r1 = sample("* * * * *", START, END, n=10, seed=42)
    r2 = sample("* * * * *", START, END, n=10, seed=42)
    assert r1.runs == r2.runs


def test_sample_different_seeds_differ():
    r1 = sample("* * * * *", START, END, n=10, seed=1)
    r2 = sample("* * * * *", START, END, n=10, seed=99)
    assert r1.runs != r2.runs


def test_sample_n_zero_returns_empty():
    result = sample("* * * * *", START, END, n=0)
    assert result.count == 0
    assert result.runs == []


def test_sample_negative_n_raises():
    with pytest.raises(ValueError):
        sample("* * * * *", START, END, n=-1)


def test_sample_first_and_last():
    result = sample("* * * * *", START, END, n=5)
    assert result.first == result.runs[0]
    assert result.last == result.runs[-1]


def test_sample_first_last_none_when_empty():
    result = sample("* * * * *", START, END, n=0)
    assert result.first is None
    assert result.last is None


def test_sample_str_contains_expression():
    result = sample("0 * * * *", START, END, n=3)
    assert "SampleResult" in str(result)


def test_sample_many_returns_list():
    results = sample_many(["* * * * *", "0 * * * *"], START, END, n=5)
    assert isinstance(results, list)
    assert len(results) == 2


def test_sample_many_all_are_sample_results():
    results = sample_many(["* * * * *", "0 * * * *"], START, END, n=5)
    assert all(isinstance(r, SampleResult) for r in results)


def test_sample_many_labels_propagated():
    results = sample_many(["* * * * *"], START, END, n=5, labels=["job-a"])
    assert results[0].label == "job-a"


def test_sample_many_label_length_mismatch_raises():
    with pytest.raises(ValueError):
        sample_many(["* * * * *", "0 * * * *"], START, END, n=5, labels=["only-one"])
