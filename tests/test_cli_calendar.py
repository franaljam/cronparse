"""Tests for cronparse.cli_calendar."""
import argparse
from unittest.mock import patch

import pytest

from cronparse.cli_calendar import add_calendar_subcommand, _cmd_calendar


@pytest.fixture
def make_parser():
    def _make():
        p = argparse.ArgumentParser()
        sub = p.add_subparsers()
        add_calendar_subcommand(sub)
        return p
    return _make


def test_add_calendar_subcommand_registers_calendar(make_parser):
    p = make_parser()
    args = p.parse_args(["calendar", "0 9 * * *"])
    assert hasattr(args, "func")


def test_calendar_default_days(make_parser):
    p = make_parser()
    args = p.parse_args(["calendar", "0 9 * * *"])
    assert args.days == 7


def test_calendar_custom_days(make_parser):
    p = make_parser()
    args = p.parse_args(["calendar", "0 9 * * *", "--days", "14"])
    assert args.days == 14


def test_calendar_label_flag(make_parser):
    p = make_parser()
    args = p.parse_args(["calendar", "0 9 * * *", "--label", "morning"])
    assert args.label == "morning"


def test_calendar_label_default_none(make_parser):
    p = make_parser()
    args = p.parse_args(["calendar", "0 9 * * *"])
    assert args.label is None


def test_cmd_calendar_prints_output(make_parser, capsys):
    p = make_parser()
    args = p.parse_args(["calendar", "0 9 * * *", "--days", "1"])
    args.func(args)
    captured = capsys.readouterr()
    assert "Calendar for" in captured.out


def test_cmd_calendar_shows_firing_hours(make_parser, capsys):
    p = make_parser()
    args = p.parse_args(["calendar", "0 9 * * *", "--days", "1"])
    args.func(args)
    captured = capsys.readouterr()
    assert "09:00" in captured.out


def test_cmd_calendar_shows_total_firing_hours(make_parser, capsys):
    p = make_parser()
    args = p.parse_args(["calendar", "0 9 * * *", "--days", "7"])
    args.func(args)
    captured = capsys.readouterr()
    assert "Total firing hours: 7" in captured.out


def test_cmd_calendar_with_label(make_parser, capsys):
    p = make_parser()
    args = p.parse_args(["calendar", "0 9 * * *", "--label", "standup"])
    args.func(args)
    captured = capsys.readouterr()
    assert "standup" in captured.out


def test_cmd_calendar_alias(make_parser, capsys):
    p = make_parser()
    args = p.parse_args(["calendar", "@daily", "--days", "2"])
    args.func(args)
    captured = capsys.readouterr()
    assert "Calendar for" in captured.out
