"""Tests for cronparse.cli_streamer."""

import argparse
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from cronparse.cli_streamer import _cmd_stream, add_streamer_subcommand


def make_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_streamer_subcommand(sub)
    return parser


def test_add_streamer_subcommand_registers_stream():
    parser = make_parser()
    args = parser.parse_args(["stream", "* * * * *"])
    assert hasattr(args, "func")


def test_stream_default_count_is_ten():
    parser = make_parser()
    args = parser.parse_args(["stream", "* * * * *"])
    assert args.count == 10


def test_stream_custom_count():
    parser = make_parser()
    args = parser.parse_args(["stream", "* * * * *", "-n", "5"])
    assert args.count == 5


def test_stream_label_flag():
    parser = make_parser()
    args = parser.parse_args(["stream", "0 * * * *", "--label", "hourly"])
    assert args.label == "hourly"


def test_stream_timezone_flag():
    parser = make_parser()
    args = parser.parse_args(["stream", "0 0 * * *", "--timezone", "US/Eastern"])
    assert args.timezone == "US/Eastern"


def test_stream_end_flag():
    parser = make_parser()
    args = parser.parse_args(["stream", "* * * * *", "--end", "2024-12-31T23:59"])
    assert args.end == "2024-12-31T23:59"


def test_cmd_stream_prints_output(capsys):
    args = argparse.Namespace(
        expression="* * * * *",
        count=3,
        end=None,
        timezone=None,
        label=None,
    )
    _cmd_stream(args)
    captured = capsys.readouterr()
    lines = [l for l in captured.out.strip().splitlines() if l]
    assert len(lines) == 3


def test_cmd_stream_label_in_output(capsys):
    args = argparse.Namespace(
        expression="* * * * *",
        count=2,
        end=None,
        timezone=None,
        label="testjob",
    )
    _cmd_stream(args)
    captured = capsys.readouterr()
    assert "[testjob]" in captured.out
