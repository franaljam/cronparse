"""Tests for cronparse.cli_windower."""

import argparse
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from cronparse.cli_windower import add_windower_subcommand, _cmd_window


@pytest.fixture()
def make_parser():
    def _make():
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_windower_subcommand(sub)
        return parser
    return _make


def test_add_windower_subcommand_registers_window(make_parser):
    parser = make_parser()
    args = parser.parse_args(["window", "* * * * *"])
    assert hasattr(args, "func")


def test_window_default_hours(make_parser):
    parser = make_parser()
    args = parser.parse_args(["window", "* * * * *"])
    assert args.hours == 24


def test_window_custom_hours(make_parser):
    parser = make_parser()
    args = parser.parse_args(["window", "* * * * *", "--hours", "6"])
    assert args.hours == 6


def test_window_label_flag(make_parser):
    parser = make_parser()
    args = parser.parse_args(["window", "0 * * * *", "--label", "hourly"])
    assert args.label == "hourly"


def test_window_start_flag(make_parser):
    parser = make_parser()
    args = parser.parse_args(["window", "* * * * *", "--start", "2024-01-15T09:00:00"])
    assert args.start == "2024-01-15T09:00:00"


def test_cmd_window_prints_output(capsys, make_parser):
    parser = make_parser()
    args = parser.parse_args([
        "window", "0 9 * * *",
        "--start", "2024-01-15T09:00:00+00:00",
        "--hours", "1",
    ])
    args.func(args)
    captured = capsys.readouterr()
    assert "0 9 * * *" in captured.out


def test_cmd_window_no_runs_message(capsys, make_parser):
    parser = make_parser()
    args = parser.parse_args([
        "window", "0 23 * * *",
        "--start", "2024-01-15T09:00:00+00:00",
        "--hours", "1",
    ])
    args.func(args)
    captured = capsys.readouterr()
    assert "no runs" in captured.out


def test_cmd_window_uses_utc_when_no_start(capsys):
    args = argparse.Namespace(
        expression="* * * * *",
        hours=1,
        start=None,
        label=None,
    )
    _cmd_window(args)
    captured = capsys.readouterr()
    assert "* * * * *" in captured.out
