"""Tests for cronparse.cli_pauser."""
import argparse
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from cronparse.cli_pauser import add_pauser_subcommand, _cmd_pause


def make_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    add_pauser_subcommand(subparsers)
    return parser


def test_add_pauser_subcommand_registers_pause():
    parser = make_parser()
    args = parser.parse_args(["pause", "* * * * *"])
    assert hasattr(args, "func")


def test_pause_default_skip_is_one():
    parser = make_parser()
    args = parser.parse_args(["pause", "* * * * *"])
    assert args.skip == 1


def test_pause_custom_skip():
    parser = make_parser()
    args = parser.parse_args(["pause", "* * * * *", "--skip", "3"])
    assert args.skip == 3


def test_pause_label_flag():
    parser = make_parser()
    args = parser.parse_args(["pause", "0 9 * * *", "--label", "morning"])
    assert args.label == "morning"


def test_pause_anchor_flag():
    parser = make_parser()
    args = parser.parse_args(
        ["pause", "* * * * *", "--anchor", "2024-06-01T10:00:00"]
    )
    assert args.anchor == "2024-06-01T10:00:00"


def test_pause_label_none_by_default():
    parser = make_parser()
    args = parser.parse_args(["pause", "* * * * *"])
    assert args.label is None


def test_pause_anchor_none_by_default():
    parser = make_parser()
    args = parser.parse_args(["pause", "* * * * *"])
    assert args.anchor is None


def test_cmd_pause_prints_output(capsys):
    parser = make_parser()
    args = parser.parse_args(
        ["pause", "* * * * *", "--anchor", "2024-01-01T00:00:00"]
    )
    args.func(args)
    captured = capsys.readouterr()
    assert "* * * * *" in captured.out


def test_cmd_pause_prints_skipped_runs(capsys):
    parser = make_parser()
    args = parser.parse_args(
        ["pause", "* * * * *", "--skip", "2", "--anchor", "2024-01-01T00:00:00"]
    )
    args.func(args)
    captured = capsys.readouterr()
    assert "Skipped runs" in captured.out


def test_cmd_pause_prints_resumes_at(capsys):
    parser = make_parser()
    args = parser.parse_args(
        ["pause", "* * * * *", "--anchor", "2024-01-01T00:00:00"]
    )
    args.func(args)
    captured = capsys.readouterr()
    assert "Resumes at" in captured.out


def test_cmd_pause_uses_now_when_no_anchor(capsys):
    """Should not raise even without --anchor."""
    parser = make_parser()
    args = parser.parse_args(["pause", "* * * * *"])
    # Should run without error
    args.func(args)
    captured = capsys.readouterr()
    assert "* * * * *" in captured.out
