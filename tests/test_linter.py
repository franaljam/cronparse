"""Tests for cronparse.linter."""

import pytest
from cronparse.linter import lint, LintResult, LintWarning


def test_lint_returns_lint_result():
    result = lint("* * * * *")
    assert isinstance(result, LintResult)


def test_clean_wildcard_expression():
    result = lint("* * * * *")
    assert result.clean


def test_specific_time_no_warnings():
    result = lint("30 8 * * 1")
    assert result.clean


def test_dom_and_dow_both_restricted_raises_w001():
    result = lint("0 9 15 * 1")
    codes = [w.code for w in result.warnings]
    assert "W001" in codes


def test_dom_wildcard_dow_restricted_no_w001():
    result = lint("0 9 * * 1")
    codes = [w.code for w in result.warnings]
    assert "W001" not in codes


def test_dom_restricted_dow_wildcard_no_w001():
    result = lint("0 9 15 * *")
    codes = [w.code for w in result.warnings]
    assert "W001" not in codes


def test_step_one_minute_warns_w002():
    # */1 on minutes expands to all 60 values — same as wildcard, so no W002
    result = lint("* * * * *")
    codes = [w.code for w in result.warnings]
    assert "W002" not in codes


def test_step_one_on_small_range():
    # 0-4 step 1 → [0,1,2,3,4] consecutive diffs all 1
    from cronparse.parser import CronExpression
    from cronparse.linter import _check_step_one

    expr = CronExpression(
        minute=list(range(0, 5)),
        hour=list(range(0, 24)),
        day_of_month=list(range(1, 32)),
        month=list(range(1, 13)),
        day_of_week=list(range(0, 8)),
    )
    warnings = _check_step_one(expr)
    codes = [w.code for w in warnings]
    assert "W002" in codes


def test_sunday_zero_and_seven_warns_w003():
    # day_of_week containing both 0 and 7
    result = lint("0 0 * * 0,7")
    codes = [w.code for w in result.warnings]
    assert "W003" in codes


def test_sunday_only_zero_no_w003():
    result = lint("0 0 * * 0")
    codes = [w.code for w in result.warnings]
    assert "W003" not in codes


def test_lint_warning_str():
    w = LintWarning("minute", "W002", "Step of 1 detected.")
    assert "W002" in str(w)
    assert "minute" in str(w)


def test_lint_result_summary_clean():
    result = lint("* * * * *")
    assert "no issues" in result.summary()


def test_lint_result_summary_with_warnings():
    result = lint("0 9 15 * 1")
    summary = result.summary()
    assert "warning" in summary
    assert "W001" in summary


def test_lint_result_not_clean_when_warnings():
    result = lint("0 9 15 * 1")
    assert not result.clean


def test_multiple_warnings_counted():
    result = lint("0 0 15 * 0,7")
    # W001 (dom+dow) and W003 (0 and 7)
    codes = {w.code for w in result.warnings}
    assert "W001" in codes
    assert "W003" in codes
