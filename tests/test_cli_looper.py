"""Tests for cronparse.cli_looper."""
import argparse
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

import pytest

from cronparse.cli_looper import add_looper_subcommand, _cmd_loop


def make_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_looper_subcommand(sub)
    return parser


def _make(expression="* * * * *", n=5, label=None):
    ns = argparse.Namespace(expression=expression, n=n, label=label)
    return ns


def test_add_looper_subcommand_registers_loop():
    parser = make_parser()
    args = parser.parse_args(["loop", "* * * * *"])
    assert hasattr(args, "func")


def test_loop_default_n():
    parser = make_parser()
    args = parser.parse_args(["loop", "*/5 * * * *"])
    assert args.n == 10


def test_loop_custom_n():
    parser = make_parser()
    args = parser.parse_args(["loop", "*/5 * * * *", "--n", "20"])
    assert args.n == 20


def test_loop_label_flag():
    parser = make_parser()
    args = parser.parse_args(["loop", "* * * * *", "--label", "test"])
    assert args.label == "test"


def test_loop_label_default_is_none():
    parser = make_parser()
    args = parser.parse_args(["loop", "* * * * *"])
    assert args.label is None


def test_cmd_loop_prints_output(capsys):
    args = _make(expression="* * * * *", n=5)
    _cmd_loop(args)
    captured = capsys.readouterr()
    assert "* * * * *" in captured.out


def test_cmd_loop_with_cycle_prints_period(capsys):
    args = _make(expression="*/5 * * * *", n=6)
    _cmd_loop(args)
    captured = capsys.readouterr()
    assert "5" in captured.out


def test_cmd_loop_no_cycle_prints_message(capsys, monkeypatch):
    from cronparse import looper as looper_mod
    from cronparse.looper import LoopResult
    from datetime import datetime, timezone

    fake_result = LoopResult(
        expression="1 2 3 4 5",
        label=None,
        cycle=None,
        runs=[],
    )
    monkeypatch.setattr(looper_mod, "loop", lambda *a, **kw: fake_result)
    args = _make(expression="1 2 3 4 5", n=2)
    _cmd_loop(args)
    captured = capsys.readouterr()
    assert "No consistent cycle" in captured.out
