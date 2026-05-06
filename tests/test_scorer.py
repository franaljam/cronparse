"""Tests for cronparse.scorer."""

import pytest

from cronparse.scorer import ScoreResult, score, score_many


def test_score_returns_score_result():
    result = score("* * * * *")
    assert isinstance(result, ScoreResult)


def test_score_full_wildcard_is_zero():
    result = score("* * * * *")
    assert result.score == 0


def test_score_specific_time_is_high():
    # minute=30, hour=9, dom=1, month=1, dow=1 — all specific
    result = score("30 9 1 1 1")
    assert result.score == 15  # 3 points × 5 fields


def test_score_hourly_expression():
    # 0 * * * * — only minute is specific
    result = score("0 * * * *")
    assert result.score == 3


def test_score_breakdown_has_five_fields():
    result = score("* * * * *")
    assert set(result.breakdown.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_score_breakdown_wildcard_fields_are_zero():
    result = score("* * * * *")
    for pts in result.breakdown.values():
        assert pts == 0


def test_score_label_stored():
    result = score("0 9 * * 1", label="Weekly Monday")
    assert result.label == "Weekly Monday"


def test_score_no_label_is_none():
    result = score("0 9 * * 1")
    assert result.label is None


def test_score_expression_stored():
    result = score("5 4 * * *")
    assert result.expression == "5 4 * * *"


def test_score_str_contains_expression():
    result = score("0 0 * * *")
    assert "0 0 * * *" in str(result)


def test_score_str_contains_score_value():
    result = score("0 0 * * *")
    assert str(result.score) in str(result)


def test_score_summary_contains_fields():
    result = score("30 9 * * *")
    summary = result.summary()
    assert "minute" in summary
    assert "hour" in summary


def test_score_many_returns_list():
    results = score_many(["* * * * *", "0 9 * * 1"])
    assert isinstance(results, list)
    assert len(results) == 2


def test_score_many_sorted_by_score_descending():
    results = score_many(["* * * * *", "0 9 1 1 1", "0 * * * *"])
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_score_many_with_labels():
    results = score_many(["* * * * *", "0 9 * * *"], labels=["A", "B"])
    labels = {r.label for r in results}
    assert labels == {"A", "B"}


def test_score_many_label_mismatch_raises():
    with pytest.raises(ValueError):
        score_many(["* * * * *", "0 9 * * *"], labels=["only-one"])


def test_score_step_expression_partial_score():
    # */15 produces 4 values out of 60 — count <= total//2 → 2 points
    result = score("*/15 * * * *")
    assert result.breakdown["minute"] == 2
