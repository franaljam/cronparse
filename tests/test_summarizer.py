"""Tests for cronparse.summarizer."""

import pytest
from cronparse.summarizer import summarize, summarize_many, report, ExpressionSummary


def test_summarize_returns_expression_summary():
    result = summarize("* * * * *")
    assert isinstance(result, ExpressionSummary)


def test_summarize_valid_expression():
    result = summarize("0 9 * * 1")
    assert result.valid is True
    assert result.errors == []


def test_summarize_human_readable_present():
    result = summarize("0 9 * * 1")
    assert len(result.human) > 0


def test_summarize_field_counts_wildcard():
    result = summarize("* * * * *")
    # wildcard expands to all valid values
    assert result.field_counts["minute"] == 60
    assert result.field_counts["hour"] == 24


def test_summarize_field_counts_specific():
    result = summarize("0 9 * * *")
    assert result.field_counts["minute"] == 1
    assert result.field_counts["hour"] == 1


def test_summarize_invalid_expression_not_valid():
    result = summarize("99 * * * *")
    assert result.valid is False
    assert len(result.errors) > 0


def test_summarize_to_dict_keys():
    result = summarize("* * * * *")
    d = result.to_dict()
    assert set(d.keys()) == {"expression", "human", "valid", "errors", "field_counts"}


def test_summarize_to_dict_values():
    result = summarize("30 6 * * *")
    d = result.to_dict()
    assert d["expression"] == "30 6 * * *"
    assert d["valid"] is True


def test_summarize_many_returns_list():
    exprs = ["* * * * *", "0 9 * * 1"]
    results = summarize_many(exprs)
    assert len(results) == 2
    assert all(isinstance(r, ExpressionSummary) for r in results)


def test_summarize_many_preserves_order():
    exprs = ["0 9 * * *", "30 18 * * *"]
    results = summarize_many(exprs)
    assert results[0].expression == exprs[0]
    assert results[1].expression == exprs[1]


def test_report_returns_string():
    output = report(["* * * * *"])
    assert isinstance(output, str)


def test_report_contains_ok_for_valid():
    output = report(["0 9 * * *"])
    assert "[OK]" in output


def test_report_contains_invalid_for_bad_expr():
    output = report(["99 * * * *"])
    assert "[INVALID]" in output


def test_report_multiple_expressions():
    output = report(["* * * * *", "0 9 * * 1"])
    assert "* * * * *" in output
    assert "0 9 * * 1" in output


def test_report_shows_human_description():
    output = report(["0 9 * * *"])
    assert "Human" in output
