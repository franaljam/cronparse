"""Tests for cronparse.nudger."""

from __future__ import annotations

import argparse

import pytest

from cronparse.nudger import NudgeResult, _nudge_minute_token, nudge
from cronparse.cli_nudger import add_nudger_subcommand


# ---------------------------------------------------------------------------
# _nudge_minute_token unit tests
# ---------------------------------------------------------------------------

def test_nudge_token_wildcard_unchanged():
    assert _nudge_minute_token("*", 5) == "*"


def test_nudge_token_specific_value():
    assert _nudge_minute_token("10", 5) == "15"


def test_nudge_token_wraps_around():
    assert _nudge_minute_token("58", 5) == "3"


def test_nudge_token_negative_offset():
    assert _nudge_minute_token("5", -3) == "2"


def test_nudge_token_negative_wraps():
    assert _nudge_minute_token("2", -5) == "57"


def test_nudge_token_step():
    assert _nudge_minute_token("0/15", 5) == "5/15"


def test_nudge_token_step_wildcard_start():
    # */5 has a non-integer start, so it falls back unchanged
    result = _nudge_minute_token("*/5", 3)
    assert result == "*/5"


def test_nudge_token_range():
    assert _nudge_minute_token("10-20", 5) == "15-25"


def test_nudge_token_list():
    assert _nudge_minute_token("0,15,30,45", 1) == "1,16,31,46"


# ---------------------------------------------------------------------------
# nudge() integration tests
# ---------------------------------------------------------------------------

def test_nudge_returns_nudge_result():
    result = nudge("0 * * * *", 5)
    assert isinstance(result, NudgeResult)


def test_nudge_stores_original_expression():
    result = nudge("0 * * * *", 5)
    assert result.original_expression == "0 * * * *"


def test_nudge_stores_offset():
    result = nudge("0 * * * *", 10)
    assert result.offset_minutes == 10


def test_nudge_label_none_by_default():
    result = nudge("0 * * * *", 5)
    assert result.label is None


def test_nudge_label_propagated():
    result = nudge("0 * * * *", 5, label="hourly")
    assert result.label == "hourly"


def test_nudge_specific_minute_shifted():
    result = nudge("0 * * * *", 5)
    assert result.expression == "5 * * * *"


def test_nudge_wildcard_minute_unchanged():
    result = nudge("* * * * *", 5)
    assert result.expression == "* * * * *"


def test_nudge_was_modified_true_when_changed():
    result = nudge("0 * * * *", 5)
    assert result.was_modified is True


def test_nudge_was_modified_false_for_wildcard():
    result = nudge("* * * * *", 10)
    assert result.was_modified is False


def test_nudge_non_minute_fields_preserved():
    result = nudge("0 9 15 6 1", 3)
    parts = result.expression.split()
    assert parts[1:] == ["9", "15", "6", "1"]


def test_nudge_tokens_list_has_five_elements():
    result = nudge("30 6 * * *", 5)
    assert len(result.nudged_tokens) == 5


def test_nudge_str_contains_expressions():
    result = nudge("0 * * * *", 5)
    s = str(result)
    assert "0 * * * *" in s
    assert "5 * * * *" in s


def test_nudge_summary_modified():
    result = nudge("0 * * * *", 5)
    assert "->" in result.summary


def test_nudge_summary_unchanged():
    result = nudge("* * * * *", 5)
    assert "unchanged" in result.summary


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_nudger_subcommand(sub)
    return p


def test_add_nudger_subcommand_registers_nudge():
    p = make_parser()
    args = p.parse_args(["nudge", "0 * * * *", "5"])
    assert hasattr(args, "func")


def test_nudge_default_summary_is_false():
    p = make_parser()
    args = p.parse_args(["nudge", "0 * * * *", "5"])
    assert args.summary is False


def test_nudge_summary_flag():
    p = make_parser()
    args = p.parse_args(["nudge", "0 * * * *", "5", "--summary"])
    assert args.summary is True


def test_nudge_label_flag():
    p = make_parser()
    args = p.parse_args(["nudge", "0 * * * *", "5", "--label", "hourly"])
    assert args.label == "hourly"


def test_cmd_nudge_prints_expression(capsys):
    p = make_parser()
    args = p.parse_args(["nudge", "0 * * * *", "5"])
    args.func(args)
    captured = capsys.readouterr()
    assert "5 * * * *" in captured.out


def test_cmd_nudge_summary_mode(capsys):
    p = make_parser()
    args = p.parse_args(["nudge", "0 * * * *", "5", "--summary"])
    args.func(args)
    captured = capsys.readouterr()
    assert "->" in captured.out
