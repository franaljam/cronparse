"""Tests for cronparse.classifier."""

import pytest

from cronparse.classifier import (
    ClassificationResult,
    CATEGORY_MINUTELY,
    CATEGORY_HOURLY,
    CATEGORY_DAILY,
    CATEGORY_WEEKLY,
    CATEGORY_MONTHLY,
    CATEGORY_CUSTOM,
    classify,
    classify_many,
)


def test_classify_returns_classification_result():
    result = classify("* * * * *")
    assert isinstance(result, ClassificationResult)


def test_classify_wildcard_is_minutely():
    result = classify("* * * * *")
    assert result.category == CATEGORY_MINUTELY


def test_classify_minutely_confidence_is_one():
    result = classify("* * * * *")
    assert result.confidence == 1.0


def test_classify_hourly_expression():
    result = classify("0 * * * *")
    assert result.category == CATEGORY_HOURLY


def test_classify_hourly_confidence_is_one():
    result = classify("0 * * * *")
    assert result.confidence == 1.0


def test_classify_daily_expression():
    result = classify("30 6 * * *")
    assert result.category == CATEGORY_DAILY


def test_classify_weekly_expression():
    result = classify("0 9 * * 1")
    assert result.category == CATEGORY_WEEKLY


def test_classify_monthly_expression():
    result = classify("0 0 1 * *")
    assert result.category == CATEGORY_MONTHLY


def test_classify_custom_expression():
    result = classify("15 10 5 3 *")
    assert result.category == CATEGORY_CUSTOM


def test_classify_stores_expression():
    result = classify("0 12 * * *")
    assert result.expression == "0 12 * * *"


def test_classify_label_none_by_default():
    result = classify("* * * * *")
    assert result.label is None


def test_classify_label_propagated():
    result = classify("0 * * * *", label="hourly-job")
    assert result.label == "hourly-job"


def test_classify_str_contains_category():
    result = classify("* * * * *")
    assert CATEGORY_MINUTELY in str(result)


def test_classify_str_contains_label():
    result = classify("0 * * * *", label="my-job")
    assert "my-job" in str(result)


def test_classify_many_returns_list():
    results = classify_many(["* * * * *", "0 * * * *"])
    assert isinstance(results, list)
    assert len(results) == 2


def test_classify_many_correct_categories():
    results = classify_many(["* * * * *", "0 * * * *", "30 6 * * *"])
    assert results[0].category == CATEGORY_MINUTELY
    assert results[1].category == CATEGORY_HOURLY
    assert results[2].category == CATEGORY_DAILY


def test_classify_many_with_labels():
    results = classify_many(["* * * * *", "0 * * * *"], labels=["a", "b"])
    assert results[0].label == "a"
    assert results[1].label == "b"


def test_classify_many_label_mismatch_raises():
    with pytest.raises(ValueError):
        classify_many(["* * * * *", "0 * * * *"], labels=["only-one"])
