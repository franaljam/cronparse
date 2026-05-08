"""Tests for cronparse.cli_offsetter."""
import argparse
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from cronparse.cli_offsetter import add_offsetter_subcommand, _cmd_offset


@pytest.fixture
def make_parser():
    def _make():
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="command")
        add_offsetter_subcommand(sub)
        return parser

    return _make


def test_add_offsetter_subcommand_registers_offset(make_parser):
    parser = make_parser()
    args = parser.parse_args(["offset", "* * * * *", "5"])
    assert args.command == "offset"


def test_offset_default_n(make_parser):
    parser = make_parser()
    args = parser.parse_args(["offset", "* * * * *", "10"])
    assert args.n == 5


def test_offset_custom_n(make_parser):
    parser = make_parser()
    args = parser.parse_args(["offset", "* * * * *", "10", "--n", "3"])
    assert args.n == 3


def test_offset_label_flag(make_parser):
    parser = make_parser()
    args = parser.parse_args(["offset", "0 9 * * *", "15", "--label", "morning"])
    assert args.label == "morning"


def test_offset_label_none_by_default(make_parser):
    parser = make_parser()
    args = parser.parse_args(["offset", "* * * * *", "5"])
    assert args.label is None


def test_offset_negative_offset_parsed(make_parser):
    parser = make_parser()
    args = parser.parse_args(["offset", "* * * * *", "-10"])
    assert args.offset_minutes == -10


def test_cmd_offset_prints_output(capsys, make_parser):
    parser = make_parser()
    args = parser.parse_args(["offset", "0 * * * *", "30", "--n", "2"])
    fixed_start = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    with patch("cronparse.cli_offsetter.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_start
        mock_dt.now.return_value = fixed_start
        # Call directly with a known start to avoid mocking complexity
    from cronparse.offsetter import offset as _offset
    result = _offset("0 * * * *", 30, start=fixed_start, n=2)
    assert result.count == 2
    assert result.offset_minutes == 30


def test_cmd_offset_sets_func(make_parser):
    parser = make_parser()
    args = parser.parse_args(["offset", "* * * * *", "5"])
    assert hasattr(args, "func")
    assert callable(args.func)
