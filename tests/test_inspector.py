"""Tests for cronparse.inspector."""

import pytest
from cronparse.inspector import inspect, InspectionReport, FieldInspection


def test_inspect_returns_inspection_report():
    report = inspect("* * * * *")
    assert isinstance(report, InspectionReport)


def test_inspect_stores_expression():
    report = inspect("0 9 * * 1")
    assert report.expression == "0 9 * * 1"


def test_inspect_has_five_fields():
    report = inspect("* * * * *")
    assert len(report.fields) == 5


def test_field_inspection_type():
    report = inspect("* * * * *")
    for f in report.fields:
        assert isinstance(f, FieldInspection)


def test_wildcard_expression_all_wildcards():
    report = inspect("* * * * *")
    assert all(f.is_wildcard for f in report.fields)


def test_specific_minute_not_wildcard():
    report = inspect("30 * * * *")
    minute = report.fields[0]
    assert not minute.is_wildcard
    assert minute.raw == "30"
    assert 30 in minute.values


def test_range_field_detected():
    report = inspect("0 9-17 * * *")
    hour = report.fields[1]
    assert hour.is_range
    assert hour.min_value == 9
    assert hour.max_value == 17


def test_step_field_detected():
    report = inspect("*/15 * * * *")
    minute = report.fields[0]
    assert minute.is_step
    assert minute.is_wildcard
    assert minute.value_count == 4


def test_list_field_detected():
    report = inspect("0 8,12,18 * * *")
    hour = report.fields[1]
    assert hour.is_list
    assert hour.value_count == 3
    assert 8 in hour.values
    assert 12 in hour.values
    assert 18 in hour.values


def test_wildcard_fields_returns_only_wildcards():
    report = inspect("0 9 * * *")
    wildcards = report.wildcard_fields()
    assert all(f.is_wildcard for f in wildcards)
    assert len(wildcards) == 3


def test_restricted_fields_returns_non_wildcards():
    report = inspect("0 9 * * *")
    restricted = report.restricted_fields()
    assert all(not f.is_wildcard for f in restricted)
    assert len(restricted) == 2


def test_field_str_contains_name_and_type():
    report = inspect("* * * * *")
    s = str(report.fields[0])
    assert "minute" in s
    assert "wildcard" in s


def test_summary_contains_expression():
    report = inspect("0 0 * * *")
    summary = report.summary()
    assert "0 0 * * *" in summary


def test_summary_contains_all_field_names():
    report = inspect("0 0 * * *")
    summary = report.summary()
    for name in ["minute", "hour", "dom", "month", "dow"]:
        assert name in summary


def test_min_max_values_for_specific():
    report = inspect("5 * * * *")
    minute = report.fields[0]
    assert minute.min_value == 5
    assert minute.max_value == 5
