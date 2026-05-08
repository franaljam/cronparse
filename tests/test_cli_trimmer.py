"""Tests for cronparse.cli_trimmer."""

import argparse
from unittest.mock import patch

import pytest

from cronparse.cli_trimmer import add_trimmer_subcommand, _cmd_trim


def make_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    add_trimmer_subcommand(subparsers)
    return parser


def test_add_trimmer_subcommand_registers_trim():
    parser = make_parser()
    args = parser.parse_args(["trim", "* * * * *"])
    assert hasattr(args, "func")


def test_trim_default_modified_only_is_false():
    parser = make_parser()
    args = parser.parse_args(["trim", "0 9 * * 1"])
    assert args.modified_only is False


def test_trim_modified_only_flag():
    parser = make_parser()
    args = parser.parse_args(["trim", "--modified-only", "0 9 * * 1"])
    assert args.modified_only is True


def test_trim_labels_flag():
    parser = make_parser()
    args = parser.parse_args(["trim", "0 9 * * 1", "--labels", "job1"])
    assert args.labels == ["job1"]


def test_trim_multiple_expressions():
    parser = make_parser()
    args = parser.parse_args(["trim", "* * * * *", "0 9 * * 1"])
    assert len(args.expression) == 2


def test_cmd_trim_prints_output(capsys):
    args = argparse.Namespace(
        expression=["0 9 * * 1"],
        labels=None,
        modified_only=False,
    )
    _cmd_trim(args)
    captured = capsys.readouterr()
    assert "0 9 * * 1" in captured.out


def test_cmd_trim_modified_only_hides_unchanged(capsys):
    args = argparse.Namespace(
        expression=["0 9 * * 1"],
        labels=None,
        modified_only=True,
    )
    _cmd_trim(args)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_cmd_trim_label_mismatch_prints_error(capsys):
    args = argparse.Namespace(
        expression=["* * * * *", "0 9 * * 1"],
        labels=["only-one"],
        modified_only=False,
    )
    _cmd_trim(args)
    captured = capsys.readouterr()
    assert "Error" in captured.out


def test_cmd_trim_with_label_shows_prefix(capsys):
    args = argparse.Namespace(
        expression=["0 9 * * 1"],
        labels=["myjob"],
        modified_only=False,
    )
    _cmd_trim(args)
    captured = capsys.readouterr()
    assert "[myjob]" in captured.out
