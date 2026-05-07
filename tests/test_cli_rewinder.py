"""Tests for cronparse.cli_rewinder."""

import argparse
from datetime import datetime
from unittest.mock import patch

import pytest

from cronparse.cli_rewinder import add_rewinder_subcommand, _cmd_rewind


def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_rewinder_subcommand(sub)
    return p


def test_add_rewinder_subcommand_registers_rewind():
    p = make_parser()
    args = p.parse_args(["rewind", "* * * * *"])
    assert hasattr(args, "func")


def test_rewind_default_count():
    p = make_parser()
    args = p.parse_args(["rewind", "* * * * *"])
    assert args.count == 5


def test_rewind_custom_count():
    p = make_parser()
    args = p.parse_args(["rewind", "* * * * *", "-n", "10"])
    assert args.count == 10


def test_rewind_label_flag():
    p = make_parser()
    args = p.parse_args(["rewind", "* * * * *", "--label", "myjob"])
    assert args.label == "myjob"


def test_rewind_before_flag():
    p = make_parser()
    args = p.parse_args(["rewind", "* * * * *", "--before", "2024-06-15T12:00:00"])
    assert args.before == "2024-06-15T12:00:00"


def test_cmd_rewind_prints_output(capsys):
    args = argparse.Namespace(
        expression="0 9 * * *",
        count=2,
        before="2024-06-15T10:00:00",
        label=None,
    )
    _cmd_rewind(args)
    captured = capsys.readouterr()
    assert "0 9 * * *" in captured.out


def test_cmd_rewind_prints_label(capsys):
    args = argparse.Namespace(
        expression="* * * * *",
        count=2,
        before="2024-06-15T12:00:00",
        label="test-job",
    )
    _cmd_rewind(args)
    captured = capsys.readouterr()
    assert "test-job" in captured.out


def test_cmd_rewind_no_before_uses_now(capsys):
    args = argparse.Namespace(
        expression="* * * * *",
        count=3,
        before=None,
        label=None,
    )
    _cmd_rewind(args)
    captured = capsys.readouterr()
    assert "Past 3 runs" in captured.out
