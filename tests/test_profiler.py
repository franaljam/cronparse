"""Tests for cronparse.profiler."""

import datetime
import pytest

from cronparse.profiler import profile, ProfileResult


START = datetime.datetime(2024, 1, 15, 0, 0, 0)


def test_profile_returns_profile_result():
    result = profile("* * * * *", start=START)
    assert isinstance(result, ProfileResult)


def test_profile_stores_expression():
    result = profile("0 * * * *", start=START)
    assert result.expression == "0 * * * *"


def test_profile_label_none_by_default():
    result = profile("* * * * *", start=START)
    assert result.label is None


def test_profile_label_propagated():
    result = profile("* * * * *", label="every minute", start=START)
    assert result.label == "every minute"


def test_profile_sample_size_matches_requested():
    result = profile("* * * * *", sample=50, start=START)
    assert result.sample_size == 50


def test_profile_every_minute_avg_gap_is_60():
    result = profile("* * * * *", sample=100, start=START)
    assert result.avg_gap_seconds == pytest.approx(60.0, abs=1.0)


def test_profile_every_minute_min_gap_is_60():
    result = profile("* * * * *", sample=100, start=START)
    assert result.min_gap_seconds == pytest.approx(60.0, abs=1.0)


def test_profile_every_minute_max_gap_is_60():
    result = profile("* * * * *", sample=100, start=START)
    assert result.max_gap_seconds == pytest.approx(60.0, abs=1.0)


def test_profile_every_minute_runs_per_day():
    result = profile("* * * * *", sample=100, start=START)
    assert result.runs_per_day == pytest.approx(1440.0, abs=1.0)


def test_profile_hourly_avg_gap_is_3600():
    result = profile("0 * * * *", sample=50, start=START)
    assert result.avg_gap_seconds == pytest.approx(3600.0, abs=1.0)


def test_profile_hourly_runs_per_day():
    result = profile("0 * * * *", sample=50, start=START)
    assert result.runs_per_day == pytest.approx(24.0, abs=0.5)


def test_profile_step_expression_gap():
    # */15 * * * * fires every 15 minutes
    result = profile("*/15 * * * *", sample=100, start=START)
    assert result.avg_gap_seconds == pytest.approx(900.0, abs=1.0)


def test_profile_sample_clamped_to_minimum():
    result = profile("* * * * *", sample=0, start=START)
    assert result.sample_size >= 2


def test_profile_str_contains_expression():
    result = profile("0 9 * * 1", start=START)
    assert "0 9 * * 1" in str(result)


def test_profile_str_contains_label():
    result = profile("0 9 * * 1", label="weekly", start=START)
    assert "weekly" in str(result)


def test_profile_str_contains_runs_per_day():
    result = profile("* * * * *", sample=60, start=START)
    assert "Runs/day" in str(result)
