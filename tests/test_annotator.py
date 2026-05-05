"""Tests for cronparse.annotator."""

import pytest
from cronparse.annotator import (
    annotate,
    AnnotatedExpression,
    FieldAnnotation,
    _classify,
)


# ---------------------------------------------------------------------------
# _classify helpers
# ---------------------------------------------------------------------------

def test_classify_wildcard():
    assert _classify("*") == "wildcard"


def test_classify_step():
    assert _classify("*/5") == "step"


def test_classify_range():
    assert _classify("1-5") == "range"


def test_classify_list():
    assert _classify("1,2,3") == "list"


def test_classify_single():
    assert _classify("30") == "single"


# ---------------------------------------------------------------------------
# annotate return type
# ---------------------------------------------------------------------------

def test_annotate_returns_annotated_expression():
    result = annotate("* * * * *")
    assert isinstance(result, AnnotatedExpression)


def test_annotate_stores_expression_string():
    result = annotate("0 9 * * 1")
    assert result.expression == "0 9 * * 1"


def test_annotate_human_is_string():
    result = annotate("0 9 * * 1")
    assert isinstance(result.human, str)
    assert len(result.human) > 0


# ---------------------------------------------------------------------------
# annotations dict
# ---------------------------------------------------------------------------

def test_annotate_has_five_fields():
    result = annotate("* * * * *")
    assert set(result.annotations.keys()) == {"minute", "hour", "day", "month", "weekday"}


def test_annotate_field_annotation_type():
    result = annotate("* * * * *")
    for ann in result.annotations.values():
        assert isinstance(ann, FieldAnnotation)


def test_annotate_wildcard_minute_note():
    result = annotate("* * * * *")
    assert result.annotations["minute"].note == "runs every minute"


def test_annotate_single_hour_note():
    result = annotate("0 9 * * *")
    assert result.annotations["hour"].note == "at a fixed hour"


def test_annotate_step_minute_note():
    result = annotate("*/15 * * * *")
    assert result.annotations["minute"].note == "every N minutes"


def test_annotate_range_day_note():
    result = annotate("0 0 1-7 * *")
    assert result.annotations["day"].note == "over a range of days"


def test_annotate_list_weekday_note():
    result = annotate("0 8 * * 1,3,5")
    assert result.annotations["weekday"].note == "on specific weekdays"


# ---------------------------------------------------------------------------
# FieldAnnotation values
# ---------------------------------------------------------------------------

def test_annotate_minute_values_wildcard():
    result = annotate("* * * * *")
    assert len(result.annotations["minute"].values) == 60


def test_annotate_hour_single_value():
    result = annotate("0 9 * * *")
    assert result.annotations["hour"].values == [9]


# ---------------------------------------------------------------------------
# summary output
# ---------------------------------------------------------------------------

def test_summary_contains_expression():
    result = annotate("0 0 * * *")
    s = result.summary()
    assert "0 0 * * *" in s


def test_summary_contains_human():
    result = annotate("0 0 * * *")
    s = result.summary()
    assert result.human in s


def test_field_annotation_str():
    ann = FieldAnnotation(field_name="minute", raw="*", values=list(range(60)), note="runs every minute")
    assert "minute" in str(ann)
    assert "runs every minute" in str(ann)
