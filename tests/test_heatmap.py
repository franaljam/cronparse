"""Tests for cronparse.heatmap."""

import datetime
import pytest

from cronparse.heatmap import build_heatmap, HeatmapResult, HeatmapCell


START = datetime.datetime(2024, 1, 1, 0, 0, 0)  # Monday


def test_build_heatmap_returns_heatmap_result():
    result = build_heatmap("* * * * *", start=START, sample_days=1)
    assert isinstance(result, HeatmapResult)


def test_build_heatmap_stores_expression():
    result = build_heatmap("0 * * * *", start=START, sample_days=1)
    assert result.expression == "0 * * * *"


def test_build_heatmap_label_none_by_default():
    result = build_heatmap("0 * * * *", start=START, sample_days=1)
    assert result.label is None


def test_build_heatmap_label_propagated():
    result = build_heatmap("0 * * * *", start=START, sample_days=1, label="hourly")
    assert result.label == "hourly"


def test_build_heatmap_sample_days_stored():
    result = build_heatmap("* * * * *", start=START, sample_days=3)
    assert result.sample_days == 3


def test_build_heatmap_grid_shape():
    result = build_heatmap("* * * * *", start=START, sample_days=1)
    assert len(result.grid) == 7
    assert all(len(row) == 24 for row in result.grid)


def test_every_minute_total_fires_equals_sample_minutes():
    days = 2
    result = build_heatmap("* * * * *", start=START, sample_days=days)
    assert result.total_fires() == days * 24 * 60


def test_hourly_total_fires_equals_sample_hours():
    days = 3
    result = build_heatmap("0 * * * *", start=START, sample_days=days)
    assert result.total_fires() == days * 24


def test_specific_time_fires_once_per_day():
    days = 7
    result = build_heatmap("30 9 * * *", start=START, sample_days=days)
    assert result.total_fires() == days


def test_specific_time_fires_in_correct_hour_bucket():
    result = build_heatmap("30 9 * * *", start=START, sample_days=7)
    total_in_hour_9 = sum(result.grid[wd][9] for wd in range(7))
    assert total_in_hour_9 == 7


def test_cell_returns_heatmap_cell():
    result = build_heatmap("0 * * * *", start=START, sample_days=1)
    cell = result.cell(0, 0)
    assert isinstance(cell, HeatmapCell)


def test_cell_values_match_grid():
    result = build_heatmap("0 * * * *", start=START, sample_days=1)
    for wd in range(7):
        for h in range(24):
            assert result.cell(wd, h).count == result.grid[wd][h]


def test_peak_returns_heatmap_cell():
    result = build_heatmap("* * * * *", start=START, sample_days=1)
    assert isinstance(result.peak(), HeatmapCell)


def test_peak_has_highest_count():
    result = build_heatmap("*/5 * * * *", start=START, sample_days=7)
    p = result.peak()
    assert p.count == max(result.grid[wd][h] for wd in range(7) for h in range(24))


def test_summary_contains_expression():
    result = build_heatmap("0 12 * * *", start=START, sample_days=7)
    assert "0 12 * * *" in result.summary()


def test_summary_contains_label_when_set():
    result = build_heatmap("0 12 * * *", start=START, sample_days=7, label="noon")
    assert "noon" in result.summary()


def test_invalid_sample_days_raises():
    with pytest.raises(ValueError):
        build_heatmap("* * * * *", start=START, sample_days=0)
