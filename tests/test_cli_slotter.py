"""Tests for cronparse.cli_slotter."""
import argparse
from unittest.mock import patch, MagicMock

import pytest

from cronparse.cli_slotter import add_slotter_subcommand, _cmd_slot


def make_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_slotter_subcommand(sub)
    return parser


def test_add_slotter_subcommand_registers_slot():
    parser = make_parser()
    args = parser.parse_args(["slot", "* * * * *"])
    assert hasattr(args, "func")


def test_slot_default_slots_is_24():
    parser = make_parser()
    args = parser.parse_args(["slot", "* * * * *"])
    assert args.slots == 24


def test_slot_custom_slots():
    parser = make_parser()
    args = parser.parse_args(["slot", "* * * * *", "--slots", "12"])
    assert args.slots == 12


def test_slot_label_flag():
    parser = make_parser()
    args = parser.parse_args(["slot", "0 * * * *", "--label", "hourly"])
    assert args.label == "hourly"


def test_slot_label_default_none():
    parser = make_parser()
    args = parser.parse_args(["slot", "0 * * * *"])
    assert args.label is None


def test_slot_date_flag():
    parser = make_parser()
    args = parser.parse_args(["slot", "* * * * *", "--date", "2024-06-01"])
    assert args.date == "2024-06-01"


def test_slot_active_only_flag():
    parser = make_parser()
    args = parser.parse_args(["slot", "* * * * *", "--active-only"])
    assert args.active_only is True


def test_slot_active_only_default_false():
    parser = make_parser()
    args = parser.parse_args(["slot", "* * * * *"])
    assert args.active_only is False


def test_cmd_slot_prints_output(capsys):
    parser = make_parser()
    args = parser.parse_args(["slot", "0 9 * * *", "--date", "2024-01-15"])
    args.func(args)
    captured = capsys.readouterr()
    assert "0 9 * * *" in captured.out


def test_cmd_slot_active_only_prints_fewer_lines(capsys):
    import datetime
    parser = make_parser()

    args_all = parser.parse_args(["slot", "0 9 * * *", "--date", "2024-01-15"])
    args_all.func(args_all)
    out_all = capsys.readouterr().out

    args_active = parser.parse_args(
        ["slot", "0 9 * * *", "--date", "2024-01-15", "--active-only"]
    )
    args_active.func(args_active)
    out_active = capsys.readouterr().out

    assert len(out_active.splitlines()) < len(out_all.splitlines())
