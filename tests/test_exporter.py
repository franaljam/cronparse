"""Tests for cronparse.exporter."""

from __future__ import annotations

import csv
import io
import json
from datetime import timezone

import pytest

from cronparse.parser import parse
from cronparse.exporter import export_json, export_csv, export_text


@pytest.fixture
def every_hour_expr():
    return parse("0 * * * *")


@pytest.fixture
def specific_expr():
    return parse("30 9 * * 1")


# --- export_json ---

def test_export_json_returns_string(every_hour_expr):
    result = export_json(every_hour_expr, n=3)
    assert isinstance(result, str)


def test_export_json_structure(every_hour_expr):
    result = json.loads(export_json(every_hour_expr, n=3))
    assert "expression" in result
    assert "human" in result
    assert "runs" in result
    assert len(result["runs"]) == 3


def test_export_json_label(every_hour_expr):
    result = json.loads(export_json(every_hour_expr, n=2, label="my-job"))
    assert result["label"] == "my-job"


def test_export_json_no_label_is_none(every_hour_expr):
    result = json.loads(export_json(every_hour_expr, n=1))
    assert result["label"] is None


def test_export_json_runs_are_iso(every_hour_expr):
    result = json.loads(export_json(every_hour_expr, n=2))
    for run in result["runs"]:
        # Should not raise
        from datetime import datetime
        datetime.fromisoformat(run)


# --- export_csv ---

def test_export_csv_returns_string(specific_expr):
    result = export_csv(specific_expr, n=3)
    assert isinstance(result, str)


def test_export_csv_has_header(specific_expr):
    result = export_csv(specific_expr, n=2)
    reader = csv.reader(io.StringIO(result))
    header = next(reader)
    assert header == ["label", "expression", "human", "run_iso"]


def test_export_csv_row_count(specific_expr):
    result = export_csv(specific_expr, n=4)
    reader = csv.reader(io.StringIO(result))
    rows = list(reader)
    # 1 header + 4 data rows
    assert len(rows) == 5


def test_export_csv_label_in_rows(specific_expr):
    result = export_csv(specific_expr, n=2, label="weekly")
    reader = csv.reader(io.StringIO(result))
    next(reader)  # skip header
    for row in reader:
        assert row[0] == "weekly"


# --- export_text ---

def test_export_text_returns_string(every_hour_expr):
    result = export_text(every_hour_expr, n=3)
    assert isinstance(result, str)


def test_export_text_contains_label(every_hour_expr):
    result = export_text(every_hour_expr, n=2, label="hourly")
    assert "hourly" in result


def test_export_text_contains_run_lines(every_hour_expr):
    result = export_text(every_hour_expr, n=3)
    assert "1." in result
    assert "3." in result


def test_export_text_no_label_skips_schedule_line(every_hour_expr):
    result = export_text(every_hour_expr, n=2)
    assert "Schedule:" not in result
