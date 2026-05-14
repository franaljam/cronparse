"""Tests for cronparse.cli_shrinker."""

import argparse
import pytest
from cronparse.cli_shrinker import add_shrinker_subcommand, _cmd_shrink


def make_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    add_shrinker_subcommand(subparsers)
    return parser


def test_add_shrinker_subcommand_registers_shrink():
    parser = make_parser()
    args = parser.parse_args(["shrink", "* * * * *"])
    assert hasattr(args, "func")


def test_shrink_default_modified_only_is_false():
    parser = make_parser()
    args = parser.parse_args(["shrink", "* * * * *"])
    assert args.modified_only is False


def test_shrink_modified_only_flag():
    parser = make_parser()
    args = parser.parse_args(["shrink", "*/1 * * * *", "--modified-only"])
    assert args.modified_only is True


def test_shrink_label_flag():
    parser = make_parser()
    args = parser.parse_args(["shrink", "* * * * *", "--label", "myjob"])
    assert args.label == "myjob"


def test_shrink_default_label_is_none():
    parser = make_parser()
    args = parser.parse_args(["shrink", "* * * * *"])
    assert args.label is None


def test_cmd_shrink_prints_output(capsys):
    parser = make_parser()
    args = parser.parse_args(["shrink", "*/1 * * * *"])
    _cmd_shrink(args)
    captured = capsys.readouterr()
    assert len(captured.out) > 0


def test_cmd_shrink_modified_only_suppresses_unchanged(capsys):
    parser = make_parser()
    args = parser.parse_args(["shrink", "* * * * *", "--modified-only"])
    _cmd_shrink(args)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_cmd_shrink_modified_only_prints_when_changed(capsys):
    parser = make_parser()
    args = parser.parse_args(["shrink", "*/1 * * * *", "--modified-only"])
    _cmd_shrink(args)
    captured = capsys.readouterr()
    assert "minute" in captured.out


def test_cmd_shrink_sets_func():
    parser = make_parser()
    args = parser.parse_args(["shrink", "* * * * *"])
    assert args.func is _cmd_shrink
