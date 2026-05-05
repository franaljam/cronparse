"""Tests for cronparse.cli_comparator module."""

import argparse
import pytest
from io import StringIO
from unittest.mock import patch

from cronparse.cli_comparator import (
    add_comparator_subcommands,
    _cmd_frequency,
    _cmd_overlap,
    _cmd_rank,
)


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_comparator_subcommands(sub)
    return parser


def test_add_comparator_subcommands_registers_frequency():
    parser = make_parser()
    args = parser.parse_args(["frequency", "* * * * *"])
    assert args.func == _cmd_frequency


def test_add_comparator_subcommands_registers_overlap():
    parser = make_parser()
    args = parser.parse_args(["overlap", "* * * * *", "0 * * * *"])
    assert args.func == _cmd_overlap


def test_add_comparator_subcommands_registers_rank():
    parser = make_parser()
    args = parser.parse_args(["rank", "* * * * *", "0 * * * *"])
    assert args.func == _cmd_rank


def test_cmd_frequency_prints_output(capsys):
    args = argparse.Namespace(expression="* * * * *")
    _cmd_frequency(args)
    captured = capsys.readouterr()
    assert "runs/hour" in captured.out
    assert "* * * * *" in captured.out


def test_cmd_overlap_no_overlap_prints_message(capsys):
    args = argparse.Namespace(
        expr_a="0 9 * * *",
        expr_b="0 10 * * *",
        window=1440,
    )
    _cmd_overlap(args)
    captured = capsys.readouterr()
    assert "overlap" in captured.out.lower()


def test_cmd_overlap_with_overlap_prints_times(capsys):
    args = argparse.Namespace(
        expr_a="*/5 * * * *",
        expr_b="*/10 * * * *",
        window=60,
    )
    _cmd_overlap(args)
    captured = capsys.readouterr()
    assert "overlap" in captured.out.lower()


def test_cmd_rank_prints_ranked_list(capsys):
    args = argparse.Namespace(expressions=["0 * * * *", "* * * * *", "0 9 * * *"])
    _cmd_rank(args)
    captured = capsys.readouterr()
    assert "1." in captured.out
    assert "2." in captured.out
    assert "3." in captured.out


def test_cmd_rank_most_frequent_listed_first(capsys):
    args = argparse.Namespace(expressions=["0 9 * * *", "* * * * *"])
    _cmd_rank(args)
    captured = capsys.readouterr()
    lines = [l for l in captured.out.splitlines() if l.strip().startswith(("1.", "2."))]
    assert "* * * * *" in lines[0]


def test_overlap_default_window_parsed():
    parser = make_parser()
    args = parser.parse_args(["overlap", "* * * * *", "0 * * * *"])
    assert args.window == 1440
