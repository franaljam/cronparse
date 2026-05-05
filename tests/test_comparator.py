"""Tests for cronparse.comparator module."""

import pytest
from datetime import datetime, timezone

from cronparse.comparator import (
    FrequencyInfo,
    OverlapResult,
    find_overlap,
    frequency,
    rank_by_frequency,
)


START = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


# --- frequency ---

def test_frequency_returns_frequency_info():
    result = frequency("* * * * *")
    assert isinstance(result, FrequencyInfo)


def test_frequency_every_minute():
    info = frequency("* * * * *")
    assert info.runs_per_hour == 60
    assert info.runs_per_day == 60 * 24


def test_frequency_every_hour():
    info = frequency("0 * * * *")
    assert info.runs_per_hour == 1
    assert info.runs_per_day == 24


def test_frequency_specific_time():
    info = frequency("30 9 * * *")
    assert info.runs_per_hour == 1
    assert info.runs_per_day == 1


def test_frequency_str_contains_expression():
    info = frequency("0 * * * *")
    assert "0 * * * *" in str(info)


def test_frequency_step_minutes():
    info = frequency("*/15 * * * *")
    assert info.runs_per_hour == 4
    assert info.runs_per_day == 4 * 24


# --- find_overlap ---

def test_find_overlap_returns_overlap_result():
    result = find_overlap("* * * * *", "* * * * *", start=START, window=5)
    assert isinstance(result, OverlapResult)


def test_find_overlap_identical_expressions_has_overlap():
    result = find_overlap("* * * * *", "* * * * *", start=START, window=10)
    assert result.has_overlap()


def test_find_overlap_non_overlapping():
    result = find_overlap("0 9 * * *", "0 10 * * *", start=START, window=1440)
    assert not result.has_overlap()


def test_find_overlap_shared_times_are_sorted():
    result = find_overlap("*/10 * * * *", "*/5 * * * *", start=START, window=60)
    times = result.shared_times
    assert times == sorted(times)


def test_find_overlap_str_no_overlap():
    result = find_overlap("0 9 * * *", "0 10 * * *", start=START, window=1440)
    assert "No overlap" in str(result)


def test_find_overlap_str_with_overlap():
    result = find_overlap("*/10 * * * *", "*/5 * * * *", start=START, window=60)
    assert "overlap" in str(result)


# --- rank_by_frequency ---

def test_rank_by_frequency_returns_list():
    result = rank_by_frequency(["* * * * *", "0 * * * *"])
    assert isinstance(result, list)
    assert len(result) == 2


def test_rank_by_frequency_most_frequent_first():
    result = rank_by_frequency(["0 * * * *", "* * * * *", "0 9 * * *"])
    assert result[0].runs_per_day >= result[1].runs_per_day >= result[2].runs_per_day


def test_rank_by_frequency_single_expression():
    result = rank_by_frequency(["*/30 * * * *"])
    assert len(result) == 1
    assert result[0].runs_per_day == 48
