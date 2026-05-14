"""Tests for cronparse.cli_zipper."""
import argparse
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

import pytest

from cronparse.cli_zipper import add_zipper_subcommand, _cmd_zip


@pytest.fixture
def make_parser():
    def _make():
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        add_zipper_subcommand(sub)
        return parser
    return _make


def test_add_zipper_subcommand_registers_zip(make_parser):
    parser = make_parser()
    args = parser.parse_args(["zip", "* * * * *"])
    assert hasattr(args, "func")


def test_zip_default_n_is_five(make_parser):
    parser = make_parser()
    args = parser.parse_args(["zip", "* * * * *"])
    assert args.n == 5


def test_zip_custom_n(make_parser):
    parser = make_parser()
    args = parser.parse_args(["zip", "* * * * *", "-n", "3"])
    assert args.n == 3


def test_zip_default_labels_is_none(make_parser):
    parser = make_parser()
    args = parser.parse_args(["zip", "* * * * *"])
    assert args.labels is None


def test_zip_custom_labels(make_parser):
    parser = make_parser()
    args = parser.parse_args(["zip", "* * * * *", "0 * * * *", "--labels", "A", "B"])
    assert args.labels == ["A", "B"]


def test_zip_multiple_expressions_parsed(make_parser):
    parser = make_parser()
    args = parser.parse_args(["zip", "* * * * *", "0 * * * *"])
    assert len(args.expressions) == 2


def test_cmd_zip_prints_output(capsys):
    args = argparse.Namespace(
        expressions=["* * * * *", "0 * * * *"],
        n=2,
        labels=None,
    )
    _cmd_zip(args)
    captured = capsys.readouterr()
    assert "[" in captured.out
    assert "expr1" in captured.out


def test_cmd_zip_uses_custom_labels(capsys):
    args = argparse.Namespace(
        expressions=["* * * * *"],
        n=2,
        labels=["my_job"],
    )
    _cmd_zip(args)
    captured = capsys.readouterr()
    assert "my_job" in captured.out
