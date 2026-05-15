"""Tests for cronparse.cli_freezer."""
from __future__ import annotations

import argparse
from unittest.mock import patch

import pytest

from cronparse.cli_freezer import add_freezer_subcommand, _cmd_freeze


def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_freezer_subcommand(sub)
    return p


def test_add_freezer_subcommand_registers_freeze():
    p = make_parser()
    args = p.parse_args(["freeze", "* * * * *"])
    assert args.command == "freeze"


def test_freeze_default_skip_is_one():
    p = make_parser()
    args = p.parse_args(["freeze", "* * * * *"])
    assert args.skip == 1


def test_freeze_default_n_is_five():
    p = make_parser()
    args = p.parse_args(["freeze", "* * * * *"])
    assert args.n == 5


def test_freeze_custom_skip():
    p = make_parser()
    args = p.parse_args(["freeze", "* * * * *", "--skip", "3"])
    assert args.skip == 3


def test_freeze_custom_n():
    p = make_parser()
    args = p.parse_args(["freeze", "* * * * *", "--n", "10"])
    assert args.n == 10


def test_freeze_label_flag():
    p = make_parser()
    args = p.parse_args(["freeze", "* * * * *", "--label", "nightly"])
    assert args.label == "nightly"


def test_freeze_sets_func():
    p = make_parser()
    args = p.parse_args(["freeze", "* * * * *"])
    assert args.func is _cmd_freeze


def test_cmd_freeze_prints_output(capsys):
    p = make_parser()
    args = p.parse_args(["freeze", "* * * * *", "--skip", "1", "--n", "3"])
    args.func(args)
    captured = capsys.readouterr()
    assert "* * * * *" in captured.out
    assert "Skipped" in captured.out


def test_cmd_freeze_label_in_output(capsys):
    p = make_parser()
    args = p.parse_args(["freeze", "* * * * *", "--label", "test-job"])
    args.func(args)
    captured = capsys.readouterr()
    assert "test-job" in captured.out
